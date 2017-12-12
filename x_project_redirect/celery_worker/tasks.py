from x_project_redirect.celery_worker import app


@app.task
def add(x, y):
    print(x + y)
    return x + y