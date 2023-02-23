$(document).ready(function () {
  // Using client-side
  var table = $("#astmOrders").DataTable({
    ajax: {
      url: "/api/orders",
      type: "GET",
      dataSrc: "",
      columnDefs: [
        {
          targets: 0,
          orderable: false,
          className: "select-checkbox",
          defaultContent: "",
        },
      ],
      select: {
        style: "os",
        selector: "td:first-child",
      },
      order: [[1, "asc"]],
    },
    columns: [
      { data: "uid" },
      { data: "created_at" },
      { data: "test_id" },
      { data: "keywork" },
      { data: "result" },
      { data: "result_date" },
      { data: "synced" },
      { data: "sync_date" },
    ],
  });

  var offcanvasElementList = [].slice.call(
    document.querySelectorAll(".offcanvas")
  );
  $("#astmOrders tbody").on("click", "tr", function () {
    selectedOrder = table.row(this).data();
    $("#astmorder").text(selectedOrder["test_id"]);
    $("#astmkeyword").text(selectedOrder["keywork"]);
    $("#astmresult").text(selectedOrder["result"]);
    $("#astmresultdate").text(selectedOrder["result_date"]);
    $("#astmcreateddate").text(selectedOrder["created_at"]);
    $("#astmsynced").text(selectedOrder["synced"]);
    $("#astmsynceddate").text(selectedOrder["sync_date"]);
    $("#astmmessage").text(selectedOrder["raw_message"]);
    console.log(selectedOrder);
    var offcanvasList = offcanvasElementList.map(function (offcanvasEl) {
      return new bootstrap.Offcanvas(offcanvasEl).show();
    });
  });
});
