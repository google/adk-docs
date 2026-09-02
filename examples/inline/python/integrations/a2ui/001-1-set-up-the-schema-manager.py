from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

schema_manager = A2uiSchemaManager(
    catalogs=[
        BasicCatalog.get_config(
            examples_path="examples",
        ),
    ],
)