import streamlit as st
import sqlite3
import html
import database as db
import utils
import views.components as components
import datetime

def show_admin_view(user):
    st.title(f"Painel Administrativo - Bem-vindo, {user[4]}")
    st.markdown("</div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Gerenciar Produtos", "Gerenciar Usuários"])

    def render_simple_table(records, columns):
        if not records:
            st.info("Sem registros para exibir.")
            return

        header = "".join(f"<th style='text-align:center; padding:8px; border-bottom:1px solid #C9981A;'>{html.escape(str(col))}</th>" for col in columns)
        rows_html = []
        for record in records:
            cells = []
            for col in columns:
                value = record.get(col, "")
                if value is None:
                    value = ""
                cells.append(f"<td style='padding:8px; border-bottom:1px solid #F3E06A; text-align:center;'>{html.escape(str(value))}</td>")
            rows_html.append("<tr>" + "".join(cells) + "</tr>")

        st.markdown(
            f"""
            <div style="overflow-x:auto; border:1px solid #C9981A; border-radius:8px; background:#FFFFFF;">
                <table style="width:100%; border-collapse:collapse;">
                    <thead><tr>{header}</tr></thead>
                    <tbody>
                        {''.join(rows_html)}
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with tab1:
        # Aniversariantes do Dia
        birthday_clients = db.get_birthday_clients()
        if birthday_clients:
            today = datetime.date.today()
            birthdays_today = []
            
            for row in birthday_clients:
                try:
                    bdate_str = str(row['birth_date'])
                    bdate = datetime.datetime.strptime(bdate_str, "%Y-%m-%d").date()
                    if bdate.month == today.month and bdate.day == today.day:
                        birthdays_today.append(row)
                except:
                    pass
            
            if birthdays_today:
                st.error(f"🎉 ATENÇÃO: HOJE É ANIVERSÁRIO DE {len(birthdays_today)} CLIENTE(S)!")
                st.markdown("""
                <div style="background-color: #F3E06A; padding: 15px; border-radius: 10px; border: 2px solid #C9981A; margin-bottom: 20px; text-align: center;">
                    <h3 style="color: #B57D0A; margin-top: 0;">🎂 Oportunidade de Venda!</h3>
                    <p style="font-size: 16px;">
                        Lembre-se de enviar uma mensagem parabenizando e <b>sugerindo a compra de um presente especial</b> da loja!
                        Ofereça um desconto ou mostre os lançamentos.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                for b_client in birthdays_today:
                    st.markdown(f"🎈 **{b_client['name']}**")
                    st.text(f"📞 Telefone: {b_client['phone'] or 'Não informado'}")
                    st.text(f"📧 Email: {b_client['email'] or 'Não informado'}")
                    st.divider()

        st.header("Visão Geral")
        products = db.get_products()
        sales = db.get_sales_report()
        
        col1, col2, col3 = st.columns(3)
        
        total_stock = sum(int(row.get('quantity') or 0) for row in products) if products else 0
        total_sold = sum(int(row.get('quantity') or 0) for row in sales) if sales else 0
        total_revenue = sum(float(row.get('total_value') or 0.0) for row in sales) if sales else 0.0
        
        with col1:
            st.metric("Produtos em Estoque", int(total_stock))
        with col2:
            st.metric("Produtos Vendidos", int(total_sold))
        with col3:
            st.metric("Receita Total", f"R$ {total_revenue:.2f}")

        # Nova linha de métricas
        st.subheader("Valores Totais")
        col4, col5 = st.columns(2)
        
        # Valor total em estoque (preço * quantidade para cada produto)
        total_stock_value = (
            sum(float(row.get('price') or 0.0) * int(row.get('quantity') or 0) for row in products)
            if products else 0.0
        )
        
        with col4:
            st.metric("Valor Total em Estoque", f"R$ {total_stock_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        # Valor total vendido formatado com destaque
        formatted_revenue = f"R$ {total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        with col5:
            st.metric("Valor Total Vendido (Receita)", formatted_revenue)
        
        st.markdown(f"""
        <div style="background-color: #F3E06A; padding: 10px; border-radius: 5px; color: #2D2D2D; font-weight: bold; margin-top: 10px; border: 1px solid #C9981A; text-align: center;">
            💰 VALOR TOTAL DOS PRODUTOS VENDIDOS: {formatted_revenue}
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Estoque vs Vendas")
        if products or sales:
            max_value = max(total_stock, total_sold, 1)
            st.markdown(
                f"""
                <div style="display:flex; flex-direction:column; gap:10px; margin-top:6px;">
                    <div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span><b>Estoque</b></span><span>{int(total_stock)}</span>
                        </div>
                        <div style="background:#F3E06A; border-radius:999px; overflow:hidden; height:16px;">
                            <div style="width:{(total_stock / max_value) * 100:.2f}%; height:100%; background:#EBCB34;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span><b>Vendidos</b></span><span>{int(total_sold)}</span>
                        </div>
                        <div style="background:#F3E06A; border-radius:999px; overflow:hidden; height:16px;">
                            <div style="width:{(total_sold / max_value) * 100:.2f}%; height:100%; background:#B57D0A;"></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
        st.subheader("Últimas Vendas")
        if sales:
            sorted_sales = sorted(sales, key=lambda row: row.get('sale_date') or '', reverse=True)
            render_simple_table(sorted_sales[:10], ["id", "product_name", "quantity", "total_value", "sale_date", "user_name"])
        else:
            st.info("Nenhuma venda registrada.")

        st.divider()
        st.subheader("Visualização Rápida de Produtos (Dashboard)")
        
        # Dashboard Product Grid (Simplified view, maybe allow sale)
        if products:
            # Area de Pesquisa no Dashboard
            search_term = st.text_input("🔍 Pesquisar Produto", placeholder="Nome, Marca, Estilo ou Tipo...", key="dash_search", label_visibility="visible")
            
            if search_term:
                products = utils.filter_products(products, search_term)

            products, total_pages, current_page = utils.paginate_dataframe(
                products, "admin_dash_products", page_size=12
            )
            st.caption(f"Mostrando página {current_page} de {total_pages}")

            cols_per_row = 4
            rows = len(products)
            
            for i in range(0, rows, cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < rows:
                        row = products[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                # Image
                                img_src = utils.get_product_image_source(row)
                                if img_src:
                                    st.image(img_src, use_container_width=True)
                                else:
                                    st.markdown("*Sem Imagem*")
                                    
                                st.markdown(f"**{row['name']}**")
                                st.caption(f"Estoque: {row['quantity']}")
                                st.markdown(f"**R$ {row['price']:.2f}**")
                                st.caption(f"Val: {row['expiration_date']}")
                                
                                # Quick Sale Action
                                if row['quantity'] > 0:
                                    with st.expander("Vender"):
                                        q_sell = st.number_input("Qtd", 1, int(row['quantity']), key=f"dash_sell_{row['id']}")
                                        if st.button("OK", key=f"dash_btn_{row['id']}"):
                                            success, msg = db.register_sale(int(row['id']), q_sell, user[0])
                                            if success:
                                                st.toast(msg, icon="✅")
                                                st.rerun()
                                            else:
                                                st.toast(msg, icon="❌")
        else:
            st.info("Nenhum produto cadastrado.")

    with tab2:
        components.render_product_management()

    with tab3:
        st.header("Gerenciar Usuários")
        with st.form("add_user"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Senha", type="password")
            new_role = st.selectbox("Função", ["admin", "funcionario", "cliente"])
            new_name = st.text_input("Nome Completo")
            
            st.markdown("---")
            st.caption("Informações Adicionais (Para Clientes)")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                new_birth_date = st.date_input("Data de Nascimento", value=None, min_value=datetime.date(1920, 1, 1), format="DD/MM/YYYY")
                new_email = st.text_input("Email")
            with col_u2:
                new_phone = st.text_input("Telefone")
                new_cpf = st.text_input("CPF")
            
            st.caption("Preferências do Cliente")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                pref_type = st.multiselect("Tipos Favoritos", utils.TIPOS)
            with col_p2:
                pref_brand = st.multiselect("Marcas Favoritas", utils.MARCAS)
            with col_p3:
                pref_style = st.multiselect("Estilos Favoritos", utils.ESTILOS)

            if st.form_submit_button("Criar Usuário"):
                if new_user and new_pass:
                    # Converter data para string
                    bdate_val = str(new_birth_date) if new_birth_date else None
                    
                    # Converter preferências
                    p_type_str = ", ".join(pref_type) if pref_type else None
                    p_brand_str = ", ".join(pref_brand) if pref_brand else None
                    p_style_str = ", ".join(pref_style) if pref_style else None
                    
                    if db.create_user(new_user, new_pass, new_role, new_name, bdate_val, new_email, new_phone, new_cpf,
                                      preferred_type=p_type_str, preferred_brand=p_brand_str, preferred_style=p_style_str):
                        st.success("Usuário criado!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar (usuário já existe?)")
                else:
                    st.error("Preencha todos os campos obrigatórios")
                    
        st.subheader("Usuários Existentes")
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, name, email, phone FROM users")
        columns = [desc[0] for desc in cursor.description]
        users_df = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        render_simple_table(users_df, ["id", "username", "role", "name", "email", "phone"])
