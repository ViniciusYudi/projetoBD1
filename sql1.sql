-- Pessoa
CREATE TABLE PESSOA (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    tipo VARCHAR(20) NOT NULL
);

-- Disciplina
CREATE TABLE DISCIPLINA (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(15) UNIQUE
);

-- Formulario
CREATE TABLE FORMULARIO (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    semestre VARCHAR(10) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL
);

-- Questao
CREATE TABLE QUESTAO (
    id SERIAL PRIMARY KEY,
    enunciado TEXT NOT NULL,
    tipo VARCHAR(10) NOT NULL
);

-- Turma
CREATE TABLE TURMA (
    id SERIAL PRIMARY KEY,
    id_professor INT NOT NULL,
    id_disciplina INT NOT NULL,
    id_formulario_padrao INT,
    semestre VARCHAR(10) NOT NULL,

    FOREIGN KEY (id_professor) REFERENCES PESSOA(id),
    FOREIGN KEY (id_disciplina) REFERENCES DISCIPLINA(id),
    FOREIGN KEY (id_formulario_padrao) REFERENCES FORMULARIO(id),

    UNIQUE (id_disciplina, semestre)
);

-- Formulario_Questao
CREATE TABLE FORMULARIO_QUESTAO (
    id_formulario INT NOT NULL,
    id_questao INT NOT NULL,
    ordem INT NOT NULL,
    valor_max_questao DECIMAL(5, 2) NOT NULL DEFAULT 0.00,

    PRIMARY KEY (id_formulario, id_questao),
    FOREIGN KEY (id_formulario) REFERENCES FORMULARIO(id),
    FOREIGN KEY (id_questao) REFERENCES QUESTAO(id)
);

-- Matricula
CREATE TABLE MATRICULA_TURMA (
    id_pessoa INT NOT NULL,
    id_turma INT NOT NULL,
    data_matricula DATE NOT NULL DEFAULT CURRENT_DATE,

    PRIMARY KEY (id_pessoa, id_turma),
    FOREIGN KEY (id_pessoa) REFERENCES PESSOA(id),
    FOREIGN KEY (id_turma) REFERENCES TURMA(id)
);

-- Submissao
CREATE TABLE SUBMISSAO (
    id BIGSERIAL PRIMARY KEY,
    id_pessoa INT NOT NULL,
    id_turma INT NOT NULL,
    id_questao INT NOT NULL,

    nota_resposta INT,
    texto_resposta TEXT,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_pessoa) REFERENCES PESSOA(id),
    FOREIGN KEY (id_turma) REFERENCES TURMA(id),
    FOREIGN KEY (id_questao) REFERENCES QUESTAO(id),

    UNIQUE (id_pessoa, id_questao, id_turma)
);

-- Formulario_Turma
CREATE TABLE FORMULARIO_TURMA (
    id SERIAL PRIMARY KEY,
    id_formulario INTEGER NOT NULL REFERENCES formulario(id),
    id_turma INTEGER NOT NULL REFERENCES turma(id),
    
    UNIQUE (id_formulario, id_turma) 
);

-- INCLUSOES ENTREG