import os
from flask import Flask, render_template, request, redirect, url_for, g
import psycopg2
import psycopg2.extras
from datetime import datetime

app = Flask(__name__)

# --- 1. CONFIGURACAO DE CONEXAO --
# ATENCAO: Nao esquecer de mudar (Leo, Vini)
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "123",
    "port": "5432"
}

def get_db_connection():
    # conecta ao banco de dados. Se uma conexao ja existir para a requisicao,
    # vai ser reutilizada no banco de dados
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"ERRO: Nao foi possivel conectar ao banco de dados: {e}")
        return None

# --- 2. ROTAS GERAIS ---
# Manter boas práticas com numeração. Aqui, processa as porradas de 
# possibilidades e trata erros com respostas para melhor interpretação.

@app.route('/')
def index():
    # Pagina inicial (tela de login/selecao de usuario)

    conn = get_db_connection()
    if conn is None:
        return "Erro de Conexao com o Banco de Dados.", 500

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "SELECT id, nome FROM PESSOA WHERE tipo = 'aluno' ORDER BY nome;"
    cursor.execute(sql)
    alunos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('login.html', alunos=alunos)


@app.route('/login', methods=['POST'])
def process_login():
    # Processa a selecao de aluno e redireciona.
    aluno_id = request.form.get('aluno_id')
    if aluno_id:
        return redirect(url_for('home_aluno', aluno_id=aluno_id))
    
    return redirect(url_for('index'))


# --- ROTAS DE ALUNO ---

@app.route('/aluno/<int:aluno_id>')
def home_aluno(aluno_id):
    # Pagina inicial do aluno. lista as turmas que ele precisa avaliar (com base em FORMULARIO_TURMA)
    # e as que ele ja avaliou (com base em SUBMISSAO).

    conn = get_db_connection()
    if conn is None:
        return "Erro de Conexao com o Banco de Dados.", 500
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT nome FROM PESSOA WHERE id = %s AND tipo = 'aluno';", (aluno_id,))
    aluno_nome_row = cursor.fetchone()
    aluno_nome = aluno_nome_row['nome'] if aluno_nome_row else "Aluno Desconhecido"

    # CONSULTA CHAVE: 
    # Busca turmas do aluno, verifica formulários atribuídos (FORMULARIO_TURMA)
    #  e status de submissao (SUBMISSAO).
    sql_turmas = """
        SELECT 
            T.id AS turma_id, 
            D.nome AS disciplina_nome, 
            P.nome AS professor_nome,
            FT.id_formulario,
            F.titulo AS formulario_titulo,
            F.data_inicio AS data_inicio_avaliacao,
            F.data_fim AS data_fim_avaliacao,
            
            -- Conta o total de questoes no formulario

            (SELECT COUNT(id_questao) FROM FORMULARIO_QUESTAO WHERE id_formulario = FT.id_formulario) AS total_questoes,
            
            -- Conta quantas questoes o aluno respondeu

            (SELECT COUNT(DISTINCT S.id_questao) 
             FROM SUBMISSAO S
             WHERE S.id_pessoa = MT.id_pessoa 
               AND S.id_turma = MT.id_turma
            ) AS questoes_respondidas,

            -- O aluno so avaliou se o numero de questoes respondidas for igual ao total
            CASE WHEN (SELECT COUNT(DISTINCT S.id_questao) 
                        FROM SUBMISSAO S
                        WHERE S.id_pessoa = MT.id_pessoa 
                          AND S.id_turma = MT.id_turma
                       ) > 0 
                     AND (SELECT COUNT(DISTINCT S.id_questao) 
                          FROM SUBMISSAO S
                          WHERE S.id_pessoa = MT.id_pessoa 
                            AND S.id_turma = MT.id_turma
                         ) = (SELECT COUNT(id_questao) 
                              FROM FORMULARIO_QUESTAO 
                              WHERE id_formulario = FT.id_formulario) 
                 THEN TRUE ELSE FALSE 
            END AS is_avaliada
            
        FROM MATRICULA_TURMA MT
        JOIN TURMA T ON MT.id_turma = T.id
        JOIN DISCIPLINA D ON T.id_disciplina = D.id
        JOIN PESSOA P ON T.id_professor = P.id
        LEFT JOIN FORMULARIO_TURMA FT ON T.id = FT.id_turma
        LEFT JOIN FORMULARIO F ON FT.id_formulario = F.id
        
        WHERE MT.id_pessoa = %s
          AND P.tipo = 'professor'
        ORDER BY is_avaliada ASC, disciplina_nome ASC;
    """

    cursor.execute(sql_turmas, (aluno_id,))
    turmas = cursor.fetchall()
    
    conn.close()

    return render_template(
        'home_aluno.html', 
        turmas=turmas, 
        aluno_id=aluno_id, 
        aluno_nome=aluno_nome
    )
    
@app.route('/aluno/<int:aluno_id>/avaliar/<int:turma_id>')
def mostrar_formulario(aluno_id, turma_id):
    # Mostra o formulario de avaliacao para uma turma especifica de um aluno,
    # buscando questoes dinamicamente pela FORMULARIO_TURMA.

    conn = get_db_connection()
    if conn is None:
        return "Erro de Conexao com o Banco de Dados.", 500
        
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Tenta encontrar o formulário atribuído à turma
    sql_form_id = """
        SELECT FT.id_formulario, F.titulo, F.data_inicio, F.data_fim
        FROM FORMULARIO_TURMA FT
        JOIN FORMULARIO F ON FT.id_formulario = F.id
        WHERE FT.id_turma = %s;
    """
    cursor.execute(sql_form_id, (turma_id,))
    form_info = cursor.fetchone()
    
    if not form_info:
        conn.close()
        return redirect(url_for('home_aluno', aluno_id=aluno_id, message="ERRO: Nenhum formulário atribuído a esta turma."))
    
    id_formulario = form_info['id_formulario']
    
    # Busca as questões desse formulário
    sql_questoes = """
        SELECT 
            Q.id, 
            Q.enunciado, 
            Q.tipo,
            FQ.ordem
        FROM FORMULARIO_QUESTAO FQ
        JOIN QUESTAO Q ON FQ.id_questao = Q.id
        WHERE FQ.id_formulario = %s
        ORDER BY FQ.ordem;
    """
    cursor.execute(sql_questoes, (id_formulario,))
    questoes_para_turma = cursor.fetchall()
    
    # Busca informações da turma para o cabeçalho
    sql_info = """
        SELECT 
            D.nome AS disciplina_nome, 
            P.nome AS professor_nome
        FROM TURMA T
        JOIN DISCIPLINA D ON T.id_disciplina = D.id
        JOIN PESSOA P ON T.id_professor = P.id
        WHERE T.id = %s;
    """
    cursor.execute(sql_info, (turma_id,))
    turma_info = cursor.fetchone()
    
    conn.close()
    
    context = {
        'aluno_id': aluno_id, 
        'turma_id': turma_id,
        'professor_nome': turma_info['professor_nome'] if turma_info else "Professor Desconhecido",
        'disciplina_nome': turma_info['disciplina_nome'] if turma_info else "Disciplina Desconhecida",
        'formulario_titulo': form_info['titulo'],
        'questoes': questoes_para_turma
    }
    return render_template('avaliacao.html', **context)


@app.route('/aluno/<int:aluno_id>/submeter/<int:turma_id>', methods=['POST'])
def submeter_avaliacao(aluno_id, turma_id):
    # Processa a submissao do formulario de avaliacao.

    conn = get_db_connection()
    if conn is None:
        print("ERRO CRITICO: Conexao com o BD falhou antes da submissao.")
        return redirect(url_for('home_aluno', aluno_id=aluno_id)) 
    
    cursor = conn.cursor()
    
    try:
        data_envio = datetime.now()
        
        for key, value in request.form.items():
            if key.startswith('resposta_'):
                try:
                    questao_id = key.split('_')[1]
                    
                    try:
                        valor_nota = int(value)
                        texto_resposta = None
                    except ValueError:
                        valor_nota = None
                        texto_resposta = value # trata como TEXTO, importantissimo
                        
                    sql_insert = """
                        INSERT INTO SUBMISSAO (id_pessoa, id_turma, id_questao, nota_resposta, texto_resposta, data_envio)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    cursor.execute(sql_insert, (
                        aluno_id, 
                        turma_id, 
                        int(questao_id), 
                        valor_nota, 
                        texto_resposta, 
                        data_envio
                    ))
                except Exception as e:
                    print(f"ERRO: Chave {key}. Erro: {e}")
                    continue

        conn.commit()
        print(f"SUCESSO: Avaliacao da Turma {turma_id} pelo Aluno {aluno_id} submetida e salva no BD.")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERRO DE DB: Falha ao salvar a avaliacao no BD. Erro: {e}")
        
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('home_aluno', aluno_id=aluno_id, message="Avaliação submetida com sucesso!"))


# --- ROTAS DE COORDENADOR ---

@app.route('/coordenador/cadastrar_questao', methods=['GET', 'POST'])
def cadastrar_questao():
    # Pagina para cadastrar uma nova questao.
    message = request.args.get('message') 
    
    if request.method == 'POST':
        enunciado = request.form['enunciado']
        try:
            tipo = request.form['tipo'].upper()
        except KeyError:
            return redirect(url_for('cadastrar_questao', message="ERRO: Tipo de questao nao fornecido."))

        conn = None
        return_message = "Questao cadastrada com sucesso!" 
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO QUESTAO (enunciado, tipo) VALUES (%s, %s);"
            cursor.execute(sql, (enunciado, tipo))
            conn.commit()
            cursor.close()
        except psycopg2.Error as e:
            return_message = f"ERRO: Erro ao cadastrar: {e}" 
        finally:
            if conn:
                conn.close()
        
        return redirect(url_for('listar_questoes', message=return_message))

    return render_template('cadastro_questao.html', message=message)

@app.route('/coordenador/listar_questoes')
def listar_questoes():
    # Pagina que lista todas as questoes cadastradas.
    message = request.args.get('message') 
    
    conn = get_db_connection()
    if conn is None:
        return "Erro de Conexao com o BD.", 500
        
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "SELECT id, enunciado, tipo FROM QUESTAO ORDER BY id DESC;"
    cursor.execute(sql)
    questoes = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('listar_questoes.html', questoes=questoes, message=message)

@app.route('/coordenador/editar_questao/<int:questao_id>', methods=['GET', 'POST'])
def editar_questao(questao_id):
    # Permite editar uma questao existente.
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('listar_questoes', message="ERRO: Conexao com o BD falhou."))

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        enunciado = request.form['enunciado']
        tipo = request.form['tipo'].upper()
        
        try:
            sql_update = "UPDATE QUESTAO SET enunciado = %s, tipo = %s WHERE id = %s;"
            cursor.execute(sql_update, (enunciado, tipo, questao_id))
            conn.commit()
            return redirect(url_for('listar_questoes', message="Questão atualizada com sucesso!"))
        except psycopg2.Error as e:
            conn.rollback()
            message = f"ERRO: Falha ao atualizar a questao: {e}"
            cursor.execute("SELECT id, enunciado, tipo FROM QUESTAO WHERE id = %s;", (questao_id,))
            questao = cursor.fetchone()
            conn.close()
            return render_template('editar_questao.html', questao=questao, message=message)
            
    else:
        cursor.execute("SELECT id, enunciado, tipo FROM QUESTAO WHERE id = %s;", (questao_id,))
        questao = cursor.fetchone()
        conn.close()
        
        if questao is None:
            return redirect(url_for('listar_questoes', message="ERRO: Questao nao encontrada."))
            
        return render_template('editar_questao.html', questao=questao, message=None)


@app.route('/coordenador/excluir_questao/<int:questao_id>', methods=['POST'])
def excluir_questao(questao_id):
    # Exclui uma questao, tem que ser existente (naturalmente kkk)
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('listar_questoes', message="ERRO: Conexao com o BD falhou."))

    cursor = conn.cursor()
    
    try:
        sql_delete = "DELETE FROM QUESTAO WHERE id = %s;"
        cursor.execute(sql_delete, (questao_id,))
        conn.commit()
        message = "Questao excluida com sucesso"
    except psycopg2.IntegrityError:
        conn.rollback()
        message = "ERRO: Nao e possivel excluir esta questao. Ela esta sendo usada em uma avaliaçao (SUBMISSAO) ou em um FORMULARIO."
    except psycopg2.Error as e:
        conn.rollback()
        message = f"ERRO: Falha ao excluir a questao: {e}"
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('listar_questoes', message=message))


@app.route('/coordenador/gerenciar_formularios', methods=['GET', 'POST'])
def gerenciar_formularios():
    # Pagina para o coordenador gerenciar e montar formularios, e buscar turmas para atribuição dele

    conn = get_db_connection()
    if conn is None:
        return "Erro de Conexao com o BD.", 500
        
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    message = request.args.get('message')
    
    # logica p/ criar o formulario
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        semestre = request.form.get('semestre')
        data_inicio_str = request.form.get('data_inicio')
        data_fim_str = request.form.get('data_fim')
        questoes_selecionadas = request.form.getlist('questao_id')
        
        if not titulo or not semestre or not data_inicio_str or not data_fim_str or not questoes_selecionadas:
            return redirect(url_for('gerenciar_formularios', message="ERRO: Todos os campos (título, datas, semestre e questões) devem ser preenchidos."))
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            
            if data_inicio > data_fim:
                 return redirect(url_for('gerenciar_formularios', message="ERRO: Data de início não pode ser posterior à data de fim."))

            # insere o novo formulario na tabela FORMULARIO
            sql_form = """
                INSERT INTO FORMULARIO (titulo, semestre, data_inicio, data_fim) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id;
            """
            cursor.execute(sql_form, (titulo, semestre, data_inicio, data_fim))
            novo_form_id = cursor.fetchone()[0] 
            
            # insere as questoes na tabela FORMULARIO_QUESTAO
            sql_rel = """
                INSERT INTO FORMULARIO_QUESTAO (id_formulario, id_questao, ordem, valor_max_questao) 
                VALUES (%s, %s, %s, %s);
            """
            for index, q_id in enumerate(questoes_selecionadas):
                ordem = index + 1
                valor_maximo = 10.00
                
                cursor.execute(sql_rel, (novo_form_id, int(q_id), ordem, valor_maximo))
            
            conn.commit()
            return redirect(url_for('gerenciar_formularios', message=f"Formulário '{titulo}' (ID {novo_form_id}) criado com sucesso!"))
            
        except ValueError:
            conn.rollback()
            message = "ERRO: O formato das datas está incorreto."
        except psycopg2.Error as e:
            conn.rollback()
            print(f"ERRO DO BANCO DE DADOS NA INSERÇÃO: {e}") 
            message = f"ERRO ao criar formulário: {e}" 

    # agora, a logica para a requisicao GET (carregar a pagina)

    sql_questoes = "SELECT id, enunciado, tipo FROM QUESTAO ORDER BY id ASC;"
    try:
        cursor.execute(sql_questoes)
        questoes = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"ERRO: Falha ao carregar questões: {e}")
        questoes = []
        message = message if message else f"ERRO ao carregar questões: {e}"

    # busca se tem formularios existentes com a consulta
    sql_formularios = 'SELECT id, titulo, semestre, data_inicio, data_fim FROM FORMULARIO ORDER BY id DESC;'
    try:
        cursor.execute(sql_formularios)
        formularios_existentes = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"ERRO: Falha ao carregar formulários: {e}")
        formularios_existentes = []
        message = f"ERRO ao carregar formulários (Verifique o schema): {e}"
        
    # busca todas as turmas disponiveis para a atribuicao
    sql_turmas = """
        SELECT 
            T.id, 
            D.nome AS disciplina_nome, 
            P.nome AS professor_nome, 
            T.semestre
        FROM TURMA T
        JOIN DISCIPLINA D ON T.id_disciplina = D.id
        JOIN PESSOA P ON T.id_professor = P.id
        ORDER BY disciplina_nome, semestre DESC;
    """
    try:
        cursor.execute(sql_turmas)
        turmas_disponiveis = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"ERRO: Falha ao carregar turmas: {e}")
        turmas_disponiveis = []
        message = f"ERRO ao carregar turmas: {e}"


    conn.close()
    
    return render_template(
        'gerenciar_formularios.html', 
        formularios=formularios_existentes,
        questoes=questoes,
        turmas=turmas_disponiveis,
        message=message
    )

@app.route('/coordenador/atribuir_formulario_turma', methods=['POST'])
def atribuir_formulario_turma():
    # Processa a atribuição de um formulário existente a uma turma.
    form_id = request.form.get('id_formulario_atribuicao')
    turma_id = request.form.get('id_turma_atribuicao')
    
    if not form_id or not turma_id:
        return redirect(url_for('gerenciar_formularios', message="ERRO: Formulário e Turma devem ser selecionados para atribuição."))

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('gerenciar_formularios', message="ERRO: Falha na conexão com o Banco de Dados."))

    cursor = conn.cursor()
    
    try:
        sql_insert = """
            INSERT INTO FORMULARIO_TURMA (id_formulario, id_turma)
            VALUES (%s, %s);
        """
        cursor.execute(sql_insert, (form_id, turma_id))
        conn.commit()
        
        #busca o nome da turma e do formulario, para a mensagem de sucesso aparecer pro usuario
        cursor.execute("SELECT titulo FROM FORMULARIO WHERE id = %s", (form_id,))
        form_titulo = cursor.fetchone()[0]
        cursor.execute("""
            SELECT D.nome || ' (' || T.semestre || ')' 
            FROM TURMA T JOIN DISCIPLINA D ON T.id_disciplina = D.id 
            WHERE T.id = %s
        """, (turma_id,))
        turma_nome = cursor.fetchone()[0]

        message = f"Formulário '{form_titulo}' atribuído à turma '{turma_nome}' com sucesso!"
        
    except psycopg2.IntegrityError:
        conn.rollback()
        message = "ERRO: Este formulário já foi atribuído a esta turma."
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERRO AO ATRIBUIR FORMULÁRIO: {e}")
        message = f"ERRO ao atribuir formulário: {e}"
        
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('gerenciar_formularios', message=message))


# --- ROTA DE PROFESSOR (TERCEIRO ENVIO, DEIXA PRA AJUSTAR DPS) --

@app.route('/professor/home')
def home_professor():
    """Pagina inicial do Professor."""
    return render_template('home_professor.html', aluno_id=None) 

# --- Execucao ---
if __name__ == '__main__':
    app.run(debug=True)