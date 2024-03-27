import os
from abc import abstractmethod

import torch
from torch.utils.tensorboard import SummaryWriter


class BaseTrainer:
    """
    Base class for all trainers
    """

    def __init__(self, params, model, optimizer, logger, dannce=True):
        self.params = params
        self.logger = logger

        self.model = model
        self.optimizer = optimizer

        self.epochs = params["epochs"]
        self.save_period = params["save_period"]

        self.start_epoch = params.get("start_epoch", 1)

        self.checkpoint_dir = (
            params["dannce_train_dir"] if dannce else params["com_train_dir"]
        )

        # setup visualization writer instance
        logdir = os.path.join(self.checkpoint_dir, "logs")
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        self.writer = SummaryWriter(log_dir=logdir)

    @abstractmethod
    def _train_epoch(self, epoch: int):
        raise NotImplementedError

    @abstractmethod
    def _valid_epoch(self, epoch: int):
        raise NotImplementedError

    @abstractmethod
    def train(self):
        """
        Full training logic
        """
        # this should never be called - probably?
        raise NotImplementedError

        for epoch in range(self.start_epoch, self.epochs + 1):
            train_loss = self._train_epoch(epoch)
            valid_loss, valid_metrics = self._valid_epoch(epoch)

            if epoch % self.save_period == 0 or epoch == self.epochs:
                self._save_checkpoint(epoch)

    def _save_checkpoint(self, epoch: int, save_best=False):
        """
        Saving checkpoints
        :param epoch: current epoch number
        :param log: logging information of the epoch
        :param save_best: if True, rename the saved checkpoint to 'model_best.pth'
        """
        state = {
            "epoch": epoch,
            "state_dict": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "params": self.params,
        }

        if epoch % self.save_period == 0 or epoch == self.epochs:
            filename = os.path.join(self.checkpoint_dir, f"checkpoint-epoch{epoch}.pth")
            self.logger.info("Saving checkpoint: {filename} ...")
        else:
            # NOTE: why is format string missing {}?
            filename = os.path.join(self.checkpoint_dir, "checkpoint.pth".format(epoch))

        torch.save(state, filename)
