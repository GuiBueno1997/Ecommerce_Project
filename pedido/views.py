from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from produto.models import Variacao
from utils import utils
from .models import Pedido, ItemPedido
from django.urls import reverse


class Pagar(DetailView):
    template_name='pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_objeto_name = 'pedido'

class SalvarPedido(View):

    template_name='pedido/pagar.html'
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Crie um perfil para finalizar a compra!')
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(self.request, 'Carrinho vazio!')
            return redirect('produto:lista')
        
        carrinho = self.request.session['carrinho']
        carrinho_variacao_ids = [v for v in carrinho]
        db_variacoes = list(
            Variacao.objects.select_related('produto').filter(
                id__in=carrinho_variacao_ids)
        )

        for variacao in db_variacoes:
            vid = str(variacao.id)

            estoque=variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']


            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * preco_unt_promo

                error_msg_estoque = 'Estoque insuficiente para alguns produtos do carrinho.'

                if error_msg_estoque:
                    messages.error(
                    self.request,
                    error_msg_estoque
                )
                return redirect('produto:carrinho')

                del carrinho[vid]
                self.request.session.save()

                return redirect('produto:carrinho')
        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_totals(carrinho)

        pedido = Pedido(
            usuario=self.request.user,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C',
        )

        pedido.save()

        ItemPedido.objects.bulk_create(
    [
        ItemPedido(
            pedido=pedido,
            produto=v['produto_nome'],
            produto_id=v['produto_id'],
            variacao=v['variacao_nome'],
            variacao_id=int(vid),
            preco=v['preco_unitario'],
            preco_promocional=v['preco_unitario_promocional'],
            quantidade=v['quantidade'],
            imagem=v['imagem'],
        )
        for vid, v in carrinho.items()
    ]
)

        del self.request.session['carrinho']
        return redirect(
            reverse(
                'pedido:pagar',
                args=[pedido.pk]
            )
        )

class Detalhe(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detalhe')

class Lista(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Lista')