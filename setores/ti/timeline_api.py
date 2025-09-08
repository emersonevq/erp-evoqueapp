from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from auth.auth_helpers import setor_required
from database import db, Chamado, ChamadoTimelineEvent, AnexoArquivo, User
from setores.ti.painel import json_response, error_response

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/api/chamados/<int:id>/timeline', methods=['GET'])
@login_required
@setor_required('Administrador')
def obter_timeline_chamado(id):
    try:
        chamado = Chamado.query.get_or_404(id)
        eventos = (
            ChamadoTimelineEvent.query
            .filter_by(chamado_id=chamado.id)
            .order_by(ChamadoTimelineEvent.criado_em.asc())
            .all()
        )
        resultado = []
        for ev in eventos:
            # Montar informação do anexo (se houver)
            anexo_info = None
            anexo_usuario_id = None
            if ev.anexo_id:
                anexo = AnexoArquivo.query.get(ev.anexo_id)
                if anexo:
                    anexo_info = {
                        'id': anexo.id,
                        'nome': anexo.nome_original,
                        'url': anexo.url_publica() if hasattr(anexo, 'url_publica') else ('/' + anexo.caminho_arquivo if anexo.caminho_arquivo else None),
                        'tamanho_kb': round((anexo.tamanho_bytes or 0) / 1024)
                    }
                    anexo_usuario_id = anexo.usuario_id

            # Determinar autor do evento
            autor_id = ev.usuario_id or anexo_usuario_id
            autor_nome = None
            if autor_id:
                u = User.query.get(autor_id)
                if u:
                    autor_nome = f"{u.nome} {u.sobrenome}".strip()

            # Classificar tipo do autor (Solicitante x Suporte)
            autor_tipo = None
            if autor_id and chamado.usuario_id:
                autor_tipo = 'Solicitante' if autor_id == chamado.usuario_id else 'Suporte'
            else:
                if ev.tipo == 'attachment_received' and not autor_id:
                    autor_tipo = 'Solicitante'
                elif ev.tipo in ['attachment_sent', 'ticket_sent'] and not autor_id:
                    autor_tipo = 'Suporte'

            item = {
                'id': ev.id,
                'tipo': ev.tipo,
                'descricao': ev.descricao,
                'status_anterior': ev.status_anterior,
                'status_novo': ev.status_novo,
                'usuario_id': autor_id,
                'usuario_nome': autor_nome,
                'autor_tipo': autor_tipo,
                'criado_em': ev.criado_em.strftime('%d/%m/%Y %H:%M:%S') if ev.criado_em else None,
                'metadados': None
            }
            if ev.metadados:
                try:
                    import json as _json
                    item['metadados'] = _json.loads(ev.metadados)
                except Exception:
                    item['metadados'] = None
            if anexo_info:
                item['anexo'] = anexo_info
            resultado.append(item)
        return json_response(resultado)
    except Exception as e:
        return error_response('Erro interno no servidor')
