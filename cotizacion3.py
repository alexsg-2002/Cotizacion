
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import pandas as pd
import os

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="Cotizador FW", layout="centered")

CONTADOR_FILE = "contador.txt"
HISTORIAL_FILE = "historial_cotizaciones.csv"
IGV_RATE = 0.18
LOGO_PATH = "/content/drive/MyDrive/Tarea_Franco/final/logo.png"

# ===============================
# CONTROL DE NÚMERO
# ===============================
def leer_contador():
    if os.path.exists(CONTADOR_FILE):
        return int(open(CONTADOR_FILE).read())
    return 1

def guardar_contador(valor):
    with open(CONTADOR_FILE, "w") as f:
        f.write(str(valor))

def guardar_historial(data):
    df = pd.DataFrame([data])
    if os.path.exists(HISTORIAL_FILE):
        df.to_csv(HISTORIAL_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(HISTORIAL_FILE, index=False)

# ===============================
# PDF
# ===============================
def generar_pdf(data):
    pdf_name = f"Cotizacion_FW_{data['numero']}_2025.pdf"
    c = canvas.Canvas(pdf_name, pagesize=A4)
    w, h = A4

    # -------------------------------
    # LOGO SUPERIOR DERECHO
    # -------------------------------
    if os.path.exists(LOGO_PATH):
        logo_width = 120   # ancho en puntos (ajustable)
        logo_height = 60   # alto en puntos (ajustable)

        c.drawImage(
            LOGO_PATH,
            w - logo_width - 50,   # margen derecho
            h - logo_height - 40,  # margen superior
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True,
            mask='auto'
        )

    # -------------------------------
    # ENCABEZADO
    # -------------------------------
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, h - 50, f"COTIZACIÓN FW-{data['numero']}-2025")

    y = h - 80
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Fecha: {data['fecha']}")

    y -= 15
    c.drawString(50, y, f"Vendedor: {data['vendedor']}")
    y -= 15
    c.drawString(50, y, f"Cliente: {data['cliente']}")
    y -= 15
    c.drawString(50, y, f"RUC: {data['ruc']}")

    # -------------------------------
    # TABLA PRODUCTOS
    # -------------------------------
    y -= 35
    #col_x = [50, 230, 340, 440, 550]
    row_h = 22

    col_prod_i, col_prod_f = 50, 260
    col_mat_i, col_mat_f = 260, 310
    col_cant_i, col_cant_f = 310, 390
    col_prec_i, col_prec_f = 390, 470
    col_tot_i, col_tot_f = 470, w - 50

    c.setFont("Helvetica-Bold", 9)
    c.drawString(col_prod_i + 4, y + 6, "PRODUCTO")
    c.drawString(col_mat_i + 4, y + 6, "TIPO MAT.")
    c.drawRightString(col_cant_f - 4, y + 6, "CANT.")
    c.drawRightString(col_prec_f - 4, y + 6, "PRECIO")
    c.drawRightString(col_tot_f - 4, y + 6, "TOTAL")
    # c.setFont("Helvetica-Bold", 9)
    # headers = ["PRODUCTO", "TIPO MAT.", "CANT.", "PRECIO", "TOTAL"]
    # for i, htxt in enumerate(headers):
    #     c.drawString(col_x[i] + 2, y + 6, htxt)

    # # Líneas cabecera
    c.line(col_prod_i, y, col_tot_f, y)
    c.line(col_prod_i, y + row_h, col_tot_f, y + row_h)
    for x in [col_prod_i, col_mat_i, col_cant_i, col_prec_i, col_tot_i, col_tot_f]:
        c.line(x, y, x, y + row_h)

    # c.line(50, y, w - 50, y)
    # c.line(50, y + row_h, w - 50, y + row_h)
    # for x in col_x:
    #     c.line(x, y, x, y + row_h)
    # c.line(w - 50, y, w - 50, y + row_h)

    # # Filas productos
    y -= row_h
    c.setFont("Helvetica", 9)

    for p in data["productos"]:
        c.drawString(col_prod_i + 4, y + 6, p["producto"])
        c.drawString(col_mat_i + 4, y + 6, p["material"])
        c.drawRightString(col_cant_f - 4, y + 6, f"{p['cantidad']:,.4f}")
        c.drawRightString(col_prec_f - 4, y + 6, f"$ {p['precio']:,.4f}")
        c.drawRightString(col_tot_f - 4, y + 6, f"$ {p['total']:,.4f}")

        c.line(col_prod_i, y, col_tot_f, y)
        for x in [col_prod_i, col_mat_i, col_cant_i, col_prec_i, col_tot_i, col_tot_f]:
            c.line(x, y, x, y + row_h)

        y -= row_h

    # for p in data["productos"]:
    #     c.drawString(col_x[0] + 2, y + 6, p["producto"])
    #     c.drawString(col_x[1] + 2, y + 6, p["material"])

    # # Números alineados a la derecha
    #     c.drawRightString(col_x[2] - 5, y + 6, f"{p['cantidad']:.4f}")
    #     c.drawRightString(col_x[3] - 5, y + 6, f"$ {p['precio']:,.4f}")
    #     c.drawRightString(col_x[4] - 5, y + 6, f"$ {p['total']:,.4f}")

    #     c.line(50, y, w - 50, y)
    #     for x in col_x:
    #         c.line(x, y, x, y + row_h)
    #     c.line(w - 50, y, w - 50, y + row_h)

    #     y -= row_h

    # -------------------------------
    # TOTALES
    # -------------------------------
    y -= 25
    c.setFont("Helvetica", 10)

    c.drawRightString(430, y, "SUBTOTAL:")
    c.drawRightString(w - 50, y, f"$ {data['subtotal']:,.4f}")

    y -= 15
    c.drawRightString(430, y, "IGV (18%):")
    c.drawRightString(w - 50, y, f"$ {data['igv']:,.4f}")

    y -= 15
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(430, y, "TOTAL:")
    c.drawRightString(w - 50, y, f"$ {data['total_final']:,.4f}")

    # -------------------------------
    # OBSERVACIONES
    # -------------------------------
    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "OBSERVACIONES:")
    y -= 15

    c.setFont("Helvetica", 9)
    for obs in data["observaciones"]:
        c.drawString(60, y, f"- {obs}")
        y -= 13

    y -= 10
    c.drawString(50, y, "Cotización válida por 30 días")

    # ==================================================
    # BLOQUE INFERIOR (PDF GUÍA)  ← AQUÍ LO QUE PEDISTE
    # ==================================================
    y -= 25
    c.drawString(50, y, "Puesto en Planta")
    y -= 13
    c.drawString(
        50, y,
        "La producción se inicia después de recibir la OC y la cancelación correspondiente."
    )
    y -= 13
    c.drawString(
        50, y,
        "Primera entrega: 40 días después de recibida la OC (Orden de Compra)."
    )

    y -= 18
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "A la espera de su grata comunicación,")

    # Firmas
    y -= 30
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "PAOLA MEDINA CHAVEZ")
    c.drawString(330, y, "ROCIO PAREDES SOTELO")

    y -= 12
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "GERENTE GENERAL")
    c.drawString(330, y, "GERENTE COMERCIAL")

    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "FULL WELL PACKAGING PERU")
    c.drawString(330, y, "FULL WELL PACKAGING PERU")

    # Empresa
    y -= 25
    c.drawString(50, y, "FULL WELL PACKAGING PERU E.I.R.L.")
    y -= 12
    c.drawString(50, y, "RUC: 20613462539")
    y -= 12
    c.drawString(50, y, "Av. Javier Prado Oeste 2158 - San Isidro")

    # Banco
    y -= 18
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "Banco de Crédito del Perú")
    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "Cuenta Corriente Dólares: 1937099120191")
    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "CCI: 00219300709912019117")

    c.save()
    return pdf_name

# ===============================
# APP STREAMLIT
# ===============================
if "cot_num" not in st.session_state:
    st.session_state.cot_num = leer_contador()

if "productos" not in st.session_state:
    st.session_state.productos = []

st.title("📄 Cotizador FULL WELL")
st.markdown(f"### Cotización: **FW-{st.session_state.cot_num}-2025**")

# -------- DATOS GENERALES --------
vendedor = st.text_input("Vendedor")
cliente = st.text_input("Cliente")
ruc = st.text_input("RUC")

st.divider()

# -------- PRODUCTOS --------
st.subheader("Agregar producto")

col1, col2 = st.columns(2)
producto = col1.text_input("Producto")
material = col2.text_input("Tipo de material")

col3, col4 = st.columns(2)
cantidad = col3.number_input("Cantidad (unidad)", min_value=0.0, format="%.4f")
precio = col4.number_input("Precio / unidad", min_value=0.0, format="%.4f")

if st.button("➕ Agregar producto"):
    st.session_state.productos.append({
        "producto": producto,
        "material": material,
        "cantidad": cantidad,
        "precio": precio,
        "total": cantidad * precio
    })

if st.session_state.productos:
    st.subheader("Productos agregados")
    st.table(pd.DataFrame(st.session_state.productos))

# -------- TOTALES --------
subtotal = sum(p["total"] for p in st.session_state.productos)
igv = subtotal * IGV_RATE
total_final = subtotal + igv

st.info(f"Subtotal: $ {subtotal:,.4f}")
st.info(f"IGV (18%): $ {igv:,.4f}")
st.success(f"TOTAL FINAL: $ {total_final:,.4f}")

# -------- OBSERVACIONES --------
obs1 = st.text_input("Observación 1", "Puesto en Planta")
obs2 = st.text_input("Observación 2", "Producción inicia tras OC")
obs3 = st.text_input("Observación 3", "Primera entrega según OC")
obs_extra = st.text_input("Observación adicional")

# -------- GENERAR PDF --------
if st.button("📥 Generar PDF"):
    data = {
        "numero": st.session_state.cot_num,
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "vendedor": vendedor,
        "cliente": cliente,
        "ruc": ruc,
        "productos": st.session_state.productos,
        "subtotal": subtotal,
        "igv": igv,
        "total_final": total_final,
        "observaciones": [o for o in [obs1, obs2, obs3, obs_extra] if o]
    }

    pdf = generar_pdf(data)
    guardar_historial(data)

    with open(pdf, "rb") as f:
        st.download_button("⬇️ Descargar PDF", f, file_name=pdf)

    st.session_state.cot_num += 1
    guardar_contador(st.session_state.cot_num)
    st.session_state.productos = []

# ===============================
# HISTORIAL
# ===============================
if os.path.exists(HISTORIAL_FILE):
    st.subheader("📊 Historial de cotizaciones")
    st.dataframe(pd.read_csv(HISTORIAL_FILE))
