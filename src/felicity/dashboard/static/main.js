document.onreadystatechange = () => {
  if (document.readyState == "complete") {
    //
    let dataset = [];
    const showPreview = (selectedOrder) => {
      var offcanvasElementList = [].slice.call(
        document.querySelectorAll(".offcanvas")
      );
      document.getElementById("astmorder").textContent =
        selectedOrder["test_id"];
      document.getElementById("astmkeyword").textContent =
        selectedOrder["keywork"];
      document.getElementById("astmresult").textContent =
        selectedOrder["result"];
      document.getElementById("astmresultdate").textContent =
        selectedOrder["result_date"];
      document.getElementById("astmcreateddate").textContent =
        selectedOrder["created_at"];
      document.getElementById("astmsynced").textContent =
        selectedOrder["synced"];
      document.getElementById("astmsynceddate").textContent =
        selectedOrder["sync_date"];
      document.getElementById("astmmessage").textContent =
        selectedOrder["raw_message"];
      console.log(selectedOrder);
      var offcanvasList = offcanvasElementList.map(function (offcanvasEl) {
        return new bootstrap.Offcanvas(offcanvasEl).show();
      });
    };

    let elem = document.getElementById("astmOrders");
    elem.innerHTML = "";
    const grid = new gridjs.Grid({
      search: true,
      columns: [
        {
          id: "orderCheckBox",
          name: "Select",
          plugin: {
            component: gridjs.plugins.selection.RowSelection,
            props: {
              id: (row) => row,
            },
          },
        },
        {
          name: "uid",
          sort: true,
        },
        {
          name: "created_at",
          sort: true,
        },
        {
          name: "test_id",
          sort: true,
        },
        {
          name: "keywork",
          sort: true,
        },
        {
          name: "result",
          sort: true,
        },
        {
          name: "result_date",
          sort: true,
        },
        {
          name: "synced",
          sort: true,
        },
        {
          name: "sync_date",
          sort: true,
        },
        {
          name: "Actions",
          formatter: (cell, row) => {
            return gridjs.h(
              "button",
              {
                className: "btn btn-primary btn-sm",
                onClick: () => {
                  const order_uid = +row.cells[1].data;
                  const index = dataset.findIndex((di) => di.uid === order_uid);
                  if (index > -1) {
                    const row = dataset[index];
                    showPreview(row);
                  }
                },
              },
              "Preview"
            );
          },
        },
      ],
      server: {
        url: "/api/orders",
        then: (data) => {
          dataset = data;
          return data.map((order) => [
            order.uid,
            order.created_at,
            order.test_id,
            order.keywork,
            order.result,
            order.result_date,
            order.synced,
            order.sync_date,
            null,
          ]);
        },
      },
      pagination: {
        limit: 10,
        summary: true,
      },
    }).render(elem);

    grid.on("ready", () => {
      const checkboxPlugin = grid.config.plugin.get("orderCheckBox");
    });

    // subscribe to the store events
    var rowIds = [];
    grid.config.store.subscribe(function (state) {
      rowIds = state.rowIds;
      console.log("checkbox updated", state);
    });

    function selectAll() {
      // grid.config.pagination.limit = 1000;
      grid.config.columns[0].data = true;
      grid.forceRender();
    }

    function deselectAll() {
      grid.config.columns[0].data = false;
      console.log(grid.config.plugin.get("orderCheckBox").props.id);
      grid.config.store.state.rowSelection.rowIds = [];
      grid.config.pagination.limit = 10;
      grid.forceRender();
    }

    // var selA = document.getElementById("selectAll");
    // if (selA.addEventListener) selA.addEventListener("click", selectAll, false);
    // else if (selA.attachEvent) selA.attachEvent("onclick", selectAll);

    // var dselA = document.getElementById("deselectAll");
    // if (dselA.addEventListener)
    //   dselA.addEventListener("click", deselectAll, false);
    // else if (dselA.attachEvent) dselA.attachEvent("onclick", deselectAll);
  }
};
