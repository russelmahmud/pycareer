from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from cached_property import cached_property
from django.conf import settings

from pycareer import log
from pycareer.job.models import Job, APPROVED, ARCHIVED, PENDING
from pycareer.services import get_service
from .base import Service
from .utils import validate, convert_to_list
from .errors import NotFoundError, IndexError
from .schema.job import JobCreateSchema, JobUpdateSchema

logger = log.get_logger('service')


class JobService(Service):
    def __init__(self):
        self.model_class = Job

    @cached_property
    def search_service(self):
        return get_service('job_search')

    def get(self, id_):
        job = self._get(id_)
        return job.to_dict()

    def create(self, job_fields):
        validated_fields = validate(JobCreateSchema(), job_fields)
        validated_fields['submitted_by'] = User.objects.get(id=validated_fields['submitted_by'])
        try:
            new_job = self.model_class(**validated_fields)
            new_job.save()
        except Exception:
            logger.exception('Exception while creating a job.')
            raise

        return new_job.to_dict()

    def update(self, id_, job_fields):
        job = self._get(id_)
        validated_fields = validate(JobUpdateSchema(), job_fields)
        for column in validated_fields.iterkeys():
            setattr(job, column, validated_fields[column])
        try:
            job.save()
        except Exception:
            logger.exception('Exception while updating the job %d' % job.id)
            raise

        return job.to_dict()

    def create_or_update(self, provider_id, job_fields):
        job = self._get_by_provider_id(provider_id)
        if job is None:
            new_job =  self.create(job_fields)
            self.publish_job(new_job)
            self.index(new_job)
            return new_job
        logger.info('Job already exists with provided_id : %s' % provider_id)

        if job.status == PENDING:
            logger.info('Job is being updated with provided_id : %s' % provider_id)
            return self.update(job.id, job_fields)

        return job.to_dict()

    def delete(self, id_):
        job = self._get(id_)
        job.delete()
        # Delete archive jobs from search engine
        self.delete_index(id_)

    def publish_job(self, job):
        job = self._get(job['id'])
        logger.info('Approving new job: %s', job.id)
        job.status = APPROVED
        job.save()
        logger.info('Approved the job: %s', job.id)

    def active_jobs(self, offset=0, limit=None):
        queryset = self.model_class.objects.filter(status=APPROVED)
        num_found = queryset.count()
        jobs = queryset.order_by('-published_at')
        jobs = jobs[offset:limit+offset] if limit else jobs[offset:]

        return {
            'items': [j.to_dict() for j in jobs],
            'num_found': num_found
        }

    def latest_jobs(self, offset=0, limit=None):
        jobs = self.model_class.objects.filter(status=APPROVED).order_by('-created_at')
        jobs = jobs[offset:limit] if limit else jobs[offset:]
        return [j.to_dict() for j in jobs]

    def archive_jobs(self):
        time_since = datetime.now() - timedelta(days=settings.LISTING_VALID_DAYS)
        jobs = self.model_class.objects.filter(status=APPROVED, published_at__lt=time_since)
        job_ids = []
        for job in jobs:
            logger.info('Archiving the job : %s' % job.id)
            job.status = ARCHIVED
            job.save()
            job_ids.append(job.id)

        # Delete archive jobs from search engine
        if job_ids:
            self.delete_index(job_ids)

    def archive(self, id_):
        self.model_class.objects.filter(id=id_).update(status=ARCHIVED)
        self.delete_index(id_)

    def index(self, job):
        logger.info('Indexing the job : %s' % job['id'])
        try:
            self.search_service.index(job)
        except IndexError:
            logger.exception('Index failed in google app engine for doc_id : %s' % job['id'])
            raise

    def delete_index(self, job_ids):
        job_ids = convert_to_list(job_ids)
        job_ids = [str(job_id) for job_id in job_ids]
        try:
            self.search_service.delete(job_ids)
        except IndexError:
            logger.exception('Index deletion failed')

    def index_jobs(self, job_ids):
        for id_ in job_ids:
            try:
                job = self.get(id_)
                self.index(job)
            except (NotFoundError, IndexError) as e:
                pass

    def my_jobs(self, user_id):
        queryset = self.model_class.objects.filter(submitted_by__id=user_id)
        num_found = queryset.count()
        jobs = queryset.order_by('-created_at')

        return {
            'items': [j.to_dict() for j in jobs if j.status != ARCHIVED],
            'num_found': num_found
        }

    def is_owner(self, job, user):
        return user.id == job['submitted_by']

    def _get(self, id_):
        try:
            job = self.model_class.objects.get(id=id_)
        except ObjectDoesNotExist:
            message = 'Job id %s does not exist.' % id_
            logger.info(message)
            raise NotFoundError(message)

        return job

    def _get_by_provider_id(self, provider_id):
        try:
            job = self.model_class.objects.get(provider_id=provider_id)
        except ObjectDoesNotExist:
            job = None

        return job
