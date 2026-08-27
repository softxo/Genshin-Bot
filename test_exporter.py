import asyncio
from pathlib import Path

from utils.exporter.engine import (
    ExporterEngine,
)

from utils.exporter.export import (
    write_export,
)


async def main():

    engine = ExporterEngine()

    result = await engine.export_all()

    output_file = Path(
        "cyrene_export.json"
    )

    output_path = write_export(
        result,
        output_file,
    )

    print(
        f"Exporter version: "
        f"{result.exporter_version}"
    )

    print(
        f"Achievements exported: "
        f"{len(result.data.get('achievements', []))}"
    )

    print(
        f"Errors: "
        f"{len(result.errors)}"
    )

    print(
        f"Export written to: "
        f"{output_path.resolve()}"
    )


if __name__ == "__main__":

    asyncio.run(main())