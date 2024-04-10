let periodo_id = document.getElementById("periodo_id").value;
function cambio_periodo() {
  var e = document.getElementById("periodos_dropdown");
  var value = e.value;
  document.getElementById("periodo_id").value = value;
}

data_init = JSON.parse(data_init.replace(/&#3/g, "!!").replace(/!!9;/g, '"'));

insertAccordion(
  "main",
  "content-data",
  Object.keys(data_init).map((e) => ({
    id: parseInt(e),
    title: data_init[e].name,
    importe: parseFloat(data_init[e].importe).toFixed(2),
  })),
  false
);

function test(e) {
  const idPartner = e.target.dataset.id;

  var requestOptions = {
    method: "GET",
    redirect: "follow",
  };

  fetch(
    `${location.origin}/my/guests/${idPartner}/${periodo_id}`,
    requestOptions
  )
    .then((response) => response.text())
    .then((result) => {
      const data = JSON.parse(result);
      console.log("data: ", data);

      subordinado = data.subordinado;

      insertAccordion(
        idPartner,
        `content-partner-${idPartner}`,
        Object.keys(subordinado).map((e) => ({
          id: parseInt(e),
          title: subordinado[e].name,
          importe: parseFloat(subordinado[e].importe).toFixed(2),
        })),
        data.sales
      );
    })
    .catch((error) => console.log("error", error));
}

function insertAccordion(code, id, items, sales) {
  console.log("EXECUTE insertAccordion");
  if (!items) return;
  var container = document.getElementById(id);
  var accordionHTML = "";
  for (var i = 0; i < items.length; i++) {
    var item = items[i];

    accordionHTML += `
      <div class="accordion-item" style="border: 1px solid rgba(0, 0, 0, 0.125)!important;">
        <h2 class="accordion-header" id="heading-${item.id}">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${item.id}" aria-expanded="false" aria-controls="#collapse-${item.id}" data-id="${item.id}" onclick="test(event)">
            ${item.title} <br/> $ ${item.importe}
          </button>
        </h2>
        <div id="collapse-${item.id}" class="accordion-collapse collapse" aria-labelledby="heading-${item.id}" data-bs-parent="#accordionExample-${code}">
          <div class="accordion-body" id="content-partner-${item.id}">
          </div>
        </div>
      </div>
    `;
  }

  let htmlContent = "";

  if (sales && sales.length > 0) {
    let rowSales = "";
    sales.forEach((element) => {
      rowSales += `
      <tr>
        <td>${element.name}</td>
        <td class="text-end">
            <span>${element.date}</span>
        </td>
        <td class="text-center">
        </td>
        <td class="text-end"><span>${element.val_comisionable}</span></td>
        <td class="text-end"><span>${element.amount_total}</span></td>
      </tr>
      `;
    });
    htmlContent += `
      <div style="border: 1px solid rgba(0, 0, 0, 0.125)!important;">
      <table class="table rounded mb-0 bg-white o_portal_my_doc_table">                    
      <thead>
          <tr class="active">
              <th>
                  <span class="d-none d-md-inline">Pedido de venta #</span>
                  <span class="d-block d-md-none">Ref.</span>
              </th>
              <th class="text-end">Fecha de pedido</th>
              <th class="text-center"></th>
              <th class="text-end">Comision</th>
              <th class="text-end">Total</th>
          </tr>
      </thead>
      <tbody>
        ${rowSales}
      </tbody>
    </table>
      </div>
      <br/>
    `;
  }

  htmlContent += `
  <div class="accordion" id="accordionExample-${code}">
    ${accordionHTML}
  </div>
  `;

  container.innerHTML = htmlContent;
}

// Ejemplo de uso:
insertAccordion("container", [
  {
    title: "Collapsible Group Item #1",
    body: "Contenido del item 1",
  },
  {
    title: "Collapsible Group Item #2",
    body: "Contenido del item 2",
  },
]);
