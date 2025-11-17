INSERT INTO FORMULARIO (titulo, semestre, data_inicio, data_fim) 
VALUES 
('Avaliação Padrão de Turma', '2025/1', '2025-03-01', '2025-07-31');

-- CADASTRA OS NOVOS ALUNOS
INSERT INTO PESSOA (nome, email, tipo) VALUES
('Leonardo Ryoichi Yakushijin Taniguti', 'leonardo.ryoichi@email.com', 'aluno'),
('Vinícius Yudi Oya', 'vinicius.oya@email.com', 'aluno'),
('Guilherme Terzioti', 'guilherme.terzioti@email.com', 'aluno'),
('Guilherme Braga', 'guilherme.braga@email.com', 'aluno'),
('Julia Yokoyama', 'julia.yokoyama@email.com', 'aluno'),
('Sofia Gutschow Casal', 'sofia.casal@email.com', 'aluno')
ON CONFLICT (email) DO NOTHING;

-- CADASTRA OS NOVOS PROFESSORES (e garante o Grande Prof. Anderson em primeiro, sem puxar saco)
INSERT INTO PESSOA (nome, email, tipo) VALUES
('Anderson Paulo Avila dos Santos', 'anderson.avila@email.com', 'professor'),
('Gustavo Taiji Naozuka', 'gustavo.naozuka@email.com', 'professor'),
('Bruno Faiçal', 'bruno.faical@email.com', 'professor'),
('Pedro Cercato', 'pedro.cercato@email.com', 'professor'),
('Paulo Natti', 'paulo.natti@email.com', 'professor')
ON CONFLICT (email) DO NOTHING;

-- CADASTRA AS NOVAS DISCIPLINAS
INSERT INTO DISCIPLINA (nome, codigo) VALUES
('Banco de Dados I', 'CDIA-BD1'),
('Laboratório de Programação', 'CDIA-LAB'),
('Inteligência Artificial', 'CDIA-IA'),
('Regressão Linear', 'CDIA-RL'),
('Equações Diferenciais Ordinárias', 'CDIA-EDO')
ON CONFLICT (codigo) DO NOTHING;

-- CRIA AS NOVAS TURMAS (todas no semestre 2025/1 e usando o formulário padrão 1)
INSERT INTO TURMA (id_professor, id_disciplina, id_formulario_padrao, semestre) VALUES
((SELECT id FROM PESSOA WHERE nome = 'Anderson Paulo Avila dos Santos'), (SELECT id FROM DISCIPLINA WHERE nome = 'Banco de Dados I'), 1, '2025/1'),
((SELECT id FROM PESSOA WHERE nome = 'Gustavo Taiji Naozuka'), (SELECT id FROM DISCIPLINA WHERE nome = 'Laboratório de Programação'), 1, '2025/1'),
((SELECT id FROM PESSOA WHERE nome = 'Bruno Faiçal'), (SELECT id FROM DISCIPLINA WHERE nome = 'Inteligência Artificial'), 1, '2025/1'),
((SELECT id FROM PESSOA WHERE nome = 'Pedro Cercato'), (SELECT id FROM DISCIPLINA WHERE nome = 'Regressão Linear'), 1, '2025/1'),
((SELECT id FROM PESSOA WHERE nome = 'Paulo Natti'), (SELECT id FROM DISCIPLINA WHERE nome = 'Equações Diferenciais Ordinárias'), 1, '2025/1')
ON CONFLICT (id_disciplina, semestre) DO NOTHING;

INSERT INTO MATRICULA_TURMA (id_pessoa, id_turma, data_matricula)
SELECT 
    P.id,
    T.id,
    CURRENT_DATE
FROM 
    PESSOA P, TURMA T
WHERE 
    P.nome IN (
        'Leonardo Ryoichi Yakushijin Taniguti',
        'Vinícius Yudi Oya',
        'Guilherme Terzioti',
        'Guilherme Braga',
        'Julia Yokoyama',
        'Sofia Gutschow Casal'
    )
AND 
    T.id_disciplina IN (
        (SELECT id FROM DISCIPLINA WHERE nome = 'Banco de Dados I'),
        (SELECT id FROM DISCIPLINA WHERE nome = 'Laboratório de Programação'),
        (SELECT id FROM DISCIPLINA WHERE nome = 'Inteligência Artificial'),
        (SELECT id FROM DISCIPLINA WHERE nome = 'Regressão Linear'),
        (SELECT id FROM DISCIPLINA WHERE nome = 'Equações Diferenciais Ordinárias')
    )
AND 
    T.semestre = '2025/1'
ON CONFLICT (id_pessoa, id_turma) DO NOTHING;
