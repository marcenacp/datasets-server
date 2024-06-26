# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The HuggingFace Authors.

from .dataset_blockages import DatasetBlockageDocument
from .jobs import JobDocument
from .lock import Lock
from .metrics import JobTotalMetricDocument, WorkerSizeJobsCountDocument
from .past_jobs import PastJobDocument


# only for the tests
def _clean_queue_database() -> None:
    """Delete all the jobs in the database"""
    JobDocument.drop_collection()  # type: ignore
    JobTotalMetricDocument.drop_collection()  # type: ignore
    WorkerSizeJobsCountDocument.drop_collection()  # type: ignore
    Lock.drop_collection()  # type: ignore
    PastJobDocument.drop_collection()  # type: ignore
    DatasetBlockageDocument.drop_collection()  # type: ignore
