from celery import shared_task

def file_naming(usr_id, file_type, file_extension):
    file_name = os.path.join(os.path.dirname(os.getcwd())) + '/proto/mainapp/static/users/{0}/{0}_{1}.{2}'.format(usr_id, file_type, file_extension)
    return file_name

@shared_task
