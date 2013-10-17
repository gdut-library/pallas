#coding: utf-8

from time import time

from flask import abort, g, current_app
from flask.ext.rq import get_connection
from rq.job import Job
from rq.exceptions import NoSuchJobError


__all__ = ['get_current_job', 'get_current_job_or_404',
           'get_current_job_progress', 'get_current_job_progress_or_404',
           'get_next_job_time', 'is_job_performable']


def get_current_job():
    '''获取用户当前进行中的同步任务'''
    job_id = g.user.get('sync_job', None)
    if job_id:
        # use default connection here
        try:
            return Job.fetch(job_id, connection=get_connection())
        except NoSuchJobError:
            # 有可能重启服务之后之前的 job 已经丢失
            return None


def get_current_job_or_404():
    '''获取用户当前进行中的同步任务

    如果没有，抛出 404
    '''
    return get_current_job() or abort(404)


def get_current_job_progress():
    '''获取当前任务的进度

    如果当前没有任务在进行，返回 None
    如果当前任务失败，返回 -1
    '''
    job = get_current_job()
    if not job:
        return None
    if job.is_failed:
        return -1

    return job.meta.get('progress', 0.0)


def get_current_job_progress_or_404():
    '''获取当前任务的进度

    如果当前没有任务在进行，抛出 404
    如果当前任务失败，返回 -1
    '''
    progress = get_current_job_progress()
    if progress is None:
        abort(404)
    return progress


def get_next_job_time():
    '''计算当前用户下次可以进行同步的时间'''
    interval = current_app.config['TASKS']['user']['update_interval']
    job = get_current_job()
    if job and job.meta.get('progress', 0) < 1:
        # 如果当前在进行更新，则应该在当前任务
        # 完成 interval 秒之后才能进行
        return time() + interval
    else:
        # 根据上次同步时间计算下次时间
        return g.user.get('last_updated', time() - interval) + interval


def is_job_performable():
    '''检查当前用户是否可以执行同步任务'''

    interval = current_app.config['TASKS']['user']['update_interval']
    if time() - g.user.get('last_updated', time()) < interval:
        return False  # 间隔太短

    job = get_current_job()
    if job and job.meta.get('progress', 1) < 1:
        return False  # 当前有任务在执行

    return True
