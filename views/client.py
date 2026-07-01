import streamlit as st
import database as db
import utils


def show_client_view(user):
    st.title(f"Catálogo de Produtos - Olá, {user[4]}")

    products = db.get_products()

    if products:
        st.sidebar.header("Filtros")
        search = st.sidebar.text_input("Buscar")

        filtered_df = products
        if search:
            filtered_df = utils.filter_products(products, search)

        cols_per_row = 3
        filtered_df, total_pages, current_page = utils.paginate_dataframe(
            filtered_df, "client_catalog", page_size=9
        )
        st.caption(f"Mostrando página {current_page} de {total_pages}")
        rows = len(filtered_df)

        for i in range(0, rows, cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < rows:
                    row = filtered_df[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            image_source = utils.get_product_image_source(row)
                            if image_source:
                                st.image(image_source, use_container_width=True)
                            else:
                                st.markdown("*Sem Imagem*")

                            st.subheader(f"<div style='text-align: center;'>{row['name']}</div>", unsafe_allow_html=True)
                            st.caption(f"<div style='text-align: center;'>{row['brand']} | {row['style']} | {row['type']}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div style='text-align: center;'>#### R$ {row['price']:.2f}</div>", unsafe_allow_html=True)

                            if row['quantity'] > 0:
                                st.success(f"<div style='text-align: center;'>Disponível ({row['quantity']})</div>", unsafe_allow_html=True)
                            else:
                                st.error("<div style='text-align: center;'>Esgotado</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum produto disponível no momento.")
