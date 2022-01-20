from typing import Any

from toml import load


class Config:
    """Helper class for grabbing config"""

    config: dict = load("./src/data/config.toml")

    def get(self, name: str) -> Any:
        """Returns specified config"""
        if name not in self.config.keys():
            raise KeyError("Config Not Found")
        else:
            return self.config[name]
