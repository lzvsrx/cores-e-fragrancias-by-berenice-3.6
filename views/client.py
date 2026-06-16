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

                            st.subheader(row['name'])
                            st.caption(f"{row['brand']} | {row['style']} | {row['type']}")
                            st.markdown(f"#### R$ {row['price']:.2f}")

                            if row['quantity'] > 0:
                                st.success(f"Disponível ({row['quantity']})")
                            else:
                                st.error("Esgotado")
    else:
        st.info("Nenhum produto disponível no momento.")
