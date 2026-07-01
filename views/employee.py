import streamlit as st
import database as db
import views.components as components
import utils
import datetime

def show_employee_view(user):
    st.title(f"Painel do Funcionário - {user[4]}")
    
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
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Ver Aniversariantes ({len(birthdays_today)})"):
                for b_client in birthdays_today:
                    st.markdown(f"🎈 **{b_client['name']}**")
                    st.text(f"📞 {b_client['phone'] or 'S/ Tel'} | 📧 {b_client['email'] or 'S/ Email'}")
                    st.divider()

    tab1, tab2 = st.tabs(["Vendas (PDV)", "Gerenciar Estoque"])
    
    with tab1:
        st.header("Ponto de Venda")
        
        products = db.get_products()
        if products:
            search_term = st.text_input("Buscar no PDV", placeholder="Digite nome, marca, tipo, id...", label_visibility="visible")
            if search_term:
                products = utils.filter_products(products, search_term)

            product_options = {f"{row['id']} - {row['name']} (Estoque: {row['quantity']})": row['id'] for row in products if int(row.get('quantity') or 0) > 0}
            
            if product_options:
                selected_option = st.selectbox("Selecione o Produto", list(product_options.keys()), label_visibility="visible")
                selected_id = product_options[selected_option]
                
                prod = db.get_product_by_id(selected_id)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if prod[8]: # image
                        st.image(prod[8], caption=prod[1], use_container_width=True)
                    else:
                        st.info("Sem imagem disponível")
                
                with col2:
                    st.write(f"**Produto:** {prod[1]}")
                    st.write(f"**Preço Unitário:** R$ {prod[5]:.2f}")
                    
                    max_qty = int(prod[6])
                    qty_sell = st.number_input("Quantidade", min_value=1, max_value=max_qty, step=1, label_visibility="visible")
                    
                    total = qty_sell * prod[5]
                    st.write(f"### Total a Pagar: R$ {total:.2f}")
                    
                    if st.button("Confirmar Venda", type="primary"):
                        success, msg = db.register_sale(selected_id, qty_sell, user[0])
                        if success:
                            st.balloons()
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.warning("Nenhum produto com estoque disponível.")
        else:
            st.warning("Sem produtos cadastrados.")

    with tab2:
        components.render_product_management()
