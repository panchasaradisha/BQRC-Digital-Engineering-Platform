"""Three-dimensional vector primitives for the BQRC platform."""

from math import sqrt

from pydantic import BaseModel, Field

from bqrc.frames.reference import ReferenceFrame


class Vector3(BaseModel):
    """A three-dimensional vector with units and reference-frame context."""

    x: float
    y: float
    z: float

    unit: str = Field(min_length=1)
    frame: ReferenceFrame

    @property
    def magnitude(self) -> float:
        """Return the Euclidean magnitude of the vector."""
        return sqrt(self.x**2 + self.y**2 + self.z**2)