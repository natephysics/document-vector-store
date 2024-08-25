from pathlib import Path
from typing import List

import hydra
from loguru import logger
from omegaconf import DictConfig


def get_hydra_config():
    return hydra.core.hydra_config.HydraConfig.get()


def configure_logging(hydra_cfg, cfg):
    # if the hydra mode is multirun, then we want to add a master log file
    if (hydra_cfg.mode is not None) and (hydra_cfg.mode.name == "MULTIRUN"):
        # Set up the master log file for the multirun (only once)
        if hydra_cfg.job.num == 0:
            # path that's up one level relative to cfg.paths.output_dir
            experiment_output_dir = Path(cfg.paths.get("output_dir")).parent

            # setup the master log file path, which will contain all the logs from the multirun
            logger.add(experiment_output_dir / "combined_runs.log", enqueue=True)

        # log the job overrides
        logger.info(
            f"Job #{hydra_cfg.job.num} with overrides: {hydra_cfg.overrides.task}"
        )

    # setup the log file path, which will contain only the logs from this specific run
    log_file_path = Path(
        cfg.paths.get("output_dir"), "logs", f"{hydra_cfg.job.name}.log"
    )
    logger_ID = logger.add(log_file_path, enqueue=True)
    return logger_ID


def instantiate_list(cfg: DictConfig, *args, **kwargs) -> List[any]:
    """Instantiate a list through hydra instantiate."""
    objects: List[any] = []
    for _, cfg_ in cfg.items():
        if "_target_" in cfg_:
            #  Add kwargs if found under configuration
            kwargs_ = {k: v for k, v in kwargs.items() if k in cfg_}
            for key, value in cfg_.items():
                cfg_[key] = value
            objects.append(hydra.utils.instantiate(cfg_, *args, **kwargs_))
    return objects
