import logging
from typing import Dict, List, Optional, TypedDict

from datasets import (
    DatasetInfo,
    get_dataset_config_info,
    get_dataset_config_names,
    get_dataset_split_names,
)
from huggingface_hub import dataset_info  # type:ignore
from huggingface_hub.utils import RepositoryNotFoundError  # type:ignore

from worker.utils import DatasetNotFoundError, SplitsNamesError

logger = logging.getLogger(__name__)


class SplitFullName(TypedDict):
    dataset_name: str
    config_name: str
    split_name: str


class SplitItem(SplitFullName):
    num_bytes: Optional[int]
    num_examples: Optional[int]


class SplitsResponse(TypedDict):
    splits: List[SplitItem]


def get_dataset_split_full_names(dataset_name: str, hf_token: Optional[str] = None) -> List[SplitFullName]:
    logger.info(f"get dataset '{dataset_name}' split full names")
    return [
        {"dataset_name": dataset_name, "config_name": config_name, "split_name": split_name}
        for config_name in get_dataset_config_names(dataset_name, use_auth_token=hf_token)
        for split_name in get_dataset_split_names(dataset_name, config_name, use_auth_token=hf_token)
    ]


def get_splits_response(
    dataset_name: str,
    hf_token: Optional[str] = None,
) -> SplitsResponse:
    """
    Get the response of /splits for one specific dataset on huggingface.co.
    Dataset can be private or gated if you pass an acceptable token.
    Args:
        dataset_name (`str`):
            A namespace (user or an organization) and a repo name separated
            by a `/`.
        hf_token (`str`, *optional*):
            An authentication token (See https://huggingface.co/settings/token)
    Returns:
        [`SplitsResponse`]: The list of splits names.
    <Tip>
    Raises the following errors:
        - [`~worker.exceptions.DatasetNotFoundError`]
          If the repository to download from cannot be found. This may be because it doesn't exist,
          or because it is set to `private` and you do not have access.
        - [`~worker.exceptions.SplitsNamesError`]
          If the list of splits could not be obtained using the datasets library.
    </Tip>
    """
    logger.info(f"get splits for dataset={dataset_name}")
    # first ensure the dataset exists on the Hub
    try:
        dataset_info(dataset_name, token=hf_token)
    except RepositoryNotFoundError as err:
        raise DatasetNotFoundError("The dataset does not exist on the Hub.") from err
    # get the list of splits
    try:
        split_full_names = get_dataset_split_full_names(dataset_name, hf_token)
    except Exception as err:
        raise SplitsNamesError("Cannot get the split names for the dataset.", cause=err) from err
    # get the number of bytes and examples for each split
    config_info: Dict[str, DatasetInfo] = {}
    split_items: List[SplitItem] = []
    for split_full_name in split_full_names:
        dataset = split_full_name["dataset_name"]
        config = split_full_name["config_name"]
        split = split_full_name["split_name"]
        try:
            if config not in config_info:
                config_info[config] = get_dataset_config_info(
                    path=dataset,
                    config_name=config,
                    use_auth_token=hf_token,
                )
            info = config_info[config]
            num_bytes = info.splits[split].num_bytes if info.splits else None
            num_examples = info.splits[split].num_examples if info.splits else None
        except Exception:
            num_bytes = None
            num_examples = None
        split_items.append(
            {
                "dataset_name": dataset,
                "config_name": config,
                "split_name": split,
                "num_bytes": num_bytes,
                "num_examples": num_examples,
            }
        )
    return {"splits": split_items}