# AGGrid for Reflex

This package provides a Reflex component wrapping the AGGrid library.

<img src="aggrid_preview.png" width="500px">

> [!WARNING]
> As it is a WorkInProgress (WIP), only some parts of the AGGrid library features are wrapped, but it should be enough for most use cases.

## Installation

```bash
pip install reflex-ag-grid
```

## Usage

```python
from reflex_ag_grid import ag_grid
```

## Helpers tools

Some implementation is offered for DataSource and handlers.

```python
from reflex_ag_grid.data_source import DataSource
from reflex_ag_grid import handlers
```


## FAQ

- **The grid doesn't appear but I don't have any compilation error. What's wrong?**

    You need to wrap your grid inside a `rx.box` or a `rx.el.div` with appropriate style for dimensions (height, width).
    
    The grid will occupy the whole space of that wrapping element.

    ```python
    rx.box(
        ag_grid(
            id="grid_1",
            row_data=data,
            column_defs=columns,
        ),
        width="50vw",
        height="50vh",
    )
    ```

- **The AGGrid feature I want is not available. What can I do?**

    This component is a partial wrapping of all the features of AGGrid. If you need a feature that is not available, 
    open an issue to request it. We will try to implement it when possible.

    If you can't wait for the team to implement it, you can also submit a PR with the feature you need.