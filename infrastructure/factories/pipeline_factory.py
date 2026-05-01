from typing import List
from application.pipeline.steps.validation_step import ValidationStep
from application.pipeline.steps.preprocess_step import PreprocessStep
from application.pipeline.pipeline import Pipeline


class PipelineFactory:
    STEP_REGISTRY = {
        "validation": ValidationStep,
        "preprocessing": PreprocessStep,
    }

    @staticmethod
    def create(pipeline_steps: List):
        steps = []
        for step_cfg in pipeline_steps:
            step_type = step_cfg["type"]
            if step_type not in PipelineFactory.STEP_REGISTRY:
                raise ValueError(f"Unknown pipeline step: {step_type}")
            steps.append(PipelineFactory.STEP_REGISTRY[step_type]())

        return Pipeline(steps)
