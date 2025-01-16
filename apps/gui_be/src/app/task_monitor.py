from celery import Celery

# Currently unimplemented!

def my_monitor(app:Celery):
    state = app.events.State()

    # def announce_failed_tasks(event):
    #     state.event(event)
    #     # task name is sent only with -received event, and state
    #     # will keep track of this for us.
    #     task = state.tasks.get(event['uuid'])

    #     print('TASK FAILED: %s[%s] %s' % (
    #         task.name, task.uuid, task.info(),))

    def announce_task_queued(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
        print(f"task sent: {task.name} { task.uuid} {task.info()}")


    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
              'task-sent': announce_task_queued,
              '*': state.event,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)
