from flask import Flask, render_template, request, redirect, url_for
import csv
import subprocess
import sys
import threading
from datetime import datetime

app = Flask(__name__)

# One refresh at a time: concurrent runs would race on the CSV files
refresh_lock = threading.Lock()

ITEMS_PER_PAGE = 20  # Number of headlines per page


@app.route('/')
def index():
    # Get the page number from the URL; non-numeric values fall back to 1
    page = request.args.get('page', 1, type=int) or 1
    # Get the selected source from the URL
    selected_source = request.args.get('source', '')

    headlines = []
    source_counts = {}  # Headline count per source, for the rail

    # Read and filter headlines labeled as 'stocks'
    with open('./headlines/result_file.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        for row in reader:
            if row[3] == 'stocks':  # Only include headlines labeled as 'stocks'
                headlines.append(row)
                source_counts[row[0]] = source_counts.get(row[0], 0) + 1

    all_count = len(headlines)
    source_counts = dict(sorted(source_counts.items()))

    # Filter headlines by the selected source if one is chosen
    if selected_source:
        headlines = [
            headline for headline in headlines if headline[0] == selected_source]

    # Tally buy/hold/sell signals across the filtered set
    signal_counts = {'buy': 0, 'hold': 0, 'sell': 0}
    for headline in headlines:
        if 'Buy' in headline[4]:
            signal_counts['buy'] += 1
        elif 'Sell' in headline[4]:
            signal_counts['sell'] += 1
        else:
            signal_counts['hold'] += 1

    total_pages = max(
        1, (len(headlines) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))

    # Calculate the start and end index for pagination
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    # Slice the headlines for the current page
    paginated_headlines = headlines[start_index:end_index]

    return render_template(
        'index.html',
        headlines=paginated_headlines,
        total_headlines=len(headlines),
        all_count=all_count,
        signal_counts=signal_counts,
        source_counts=source_counts,
        selected_source=selected_source,
        page=page,
        total_pages=total_pages,
        today=datetime.now().strftime('%A, %d %B %Y')
    )


@app.route('/stories')
def stories():
    import storyline
    return render_template('stories.html', stories=storyline.list_stories())


@app.route('/story/<int:story_id>')
def story_detail(story_id):
    import storyline
    import json
    view = storyline.story_view(story_id)
    if view is None:
        return redirect(url_for('stories'))

    source_names = sorted({a['source_name'] for a in view['articles']})
    articles_by_id = {a['id']: a for a in view['articles']}
    claims = []
    if view['latest']:
        for claim in json.loads(view['latest']['claims']):
            names = sorted({articles_by_id[i]['source_name']
                            for i in claim['evidence_ids'] if i in articles_by_id})
            claims.append({'text': claim['text'], 'source_names': names})
    return render_template('story.html', view=view,
                           source_names=source_names, claims=claims)


@app.route('/story/<int:story_id>/read', methods=['POST'])
def story_mark_read(story_id):
    import storyline
    version_id = request.form.get('version_id', type=int)
    if version_id:
        storyline.mark_read(story_id, version_id)
    return redirect(url_for('story_detail', story_id=story_id))


@app.route('/run_script', methods=['POST'])
def run_script():
    if not refresh_lock.acquire(blocking=False):
        return 'A refresh is already running. Try again in a minute.', 409
    try:
        subprocess.run([sys.executable, "./mainFile.py"], check=True)
    except subprocess.CalledProcessError as e:
        return f'The scraper failed (exit code {e.returncode}). Check the server log.', 500
    finally:
        refresh_lock.release()

    # After a successful run, redirect back to the homepage
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
