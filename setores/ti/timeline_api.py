from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from auth.auth_helpers import setor_required
from database import db, Chamado, ChamadoTimelineEvent, AnexoArquivo
from setores.ti.painel import json_response, error_response

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/api/chamados/<int:id>/timeline', methods=['GET'])
@login_required
@setor_required('Administrador')
def obter_timeline_chamado(id):
    try:
        chamado = Chamado.query.get_or_404(id)
        eventos = ChamadoTimelineEvent.query.filter_by(chamado_id=chamado.id).order_by(ChamadoTimelineEvent.criado_em.asc()).all()
        resultado = []
        for ev in eventos:
            item = {
                'id': ev.id,
                'tipo': ev.tipo,
                'descricao': ev.descricao,
                'status_anterior': ev.status_anterior,
                'status_novo': ev.status_novo,
                'usuario_id': ev.usuario_id,
                'criado_em': ev.criado_em.strftime('%d/%m/%Y %H:%M:%S') if ev.criado_em else None,
            }
            if ev.anexo_id:
                anexo = AnexoArquivo.query.get(ev.anexo_id)
                if anexo:
                    item['anexo'] = {
                        'id': anexo.id,
                        'nome': anexo.nome_original,
                        'url': anexo.url_publica() if hasattr(anexo, 'url_publica') else ('/' + anexo.caminho_arquivo if anexo.caminho_arquivo else None),
                        'tamanho_kb': round((anexo.tamanho_bytes or 0) / 1024)
                    }
            resultado.append(item)
        return json_response(resultado)
    except Exception as e:
        return error_response('Erro interno no servidor')
