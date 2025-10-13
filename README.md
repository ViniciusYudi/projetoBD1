# projetoBD1
Projeto da Disciplina de Banco de Dados 1

Trabalho Banco de Dados

Alunos:
Leonardo Ryoichi Yakushijin Taniguti
Vinícius Yudi Oya

1. Ideia Central do Sistema
A ideia do projeto é uma Plataforma de Feedback Acadêmico, um sistema online simples para que alunos possam dar suas opiniões sobre as materias que cursaram e seus professores ao final de cada semestre. A ideia é que a coordenação possa usar esses dados para entender melhor o que esta funcionando e onde podem ocorrer melhorias. Tudo sera anonimo para os alunos.

2. Como Funciona (Funcionalidades)
O sistema terá três tipos de acesso: Coordenador, Aluno e Professor.

-> Para o Coordenador:
   
a.	Monta os Formulários: Ele cadastra as perguntas que serao usadas nos formulários de feedback (ex: "O professor domina o conteúdo?").
b.	Abre o Periodo de Feedback: Ele cria um novo "Periodo de Feedback" (ex: "Feedback Semestre 2025.2"), define as datas de inicio e fim.
c.	Define o que sera avaliado: Associa as turmas (materia + professor) que participarão desse periodo de feedback.
d.	Analisa os Resultados: Depois que o prazo acaba, o coordenador acessa graficos e tabelas com as medias gerais, os comentarios, e consegue comparar o desenpenho entre diferentes areas ou materias.
   
-> Para o Aluno:

a.	Entra no Sistema: Faz login com sua matricula.
b.	Vê o que Precisa Avaliar: Uma lista mostra quais das suas materias estão com feedback aberto.
c.	Responde: Ele clica em uma materia, responde às perguntas de multipla escolha e deixa comentarios, se quizer.
d.	Envia: As respostas sao salvas sem nenhuma identificação de quem as enviou.

-> Para o Professor:

a.	Acessa seus Resultados: O professor pode ver um resumo do seu proprio desempenho, com médias e gráficos, mas sem saber quem respondeu o quê.

3. Relatórios Gerados pelo Sistema
Os relatórios são o coração do projeto. Eles precisam de comandos SQL mais elaborados para funcionar.

Relatório 1: Painel Geral do Semestre (Visão do Coordenador)

->	O que mostra? Um resumo de como foi o feedback de todas as materias no semestre.
->	Como?
  ->	Gráfico de Barras: Comparando a nota media de diferentes departamentos (ex: Humanas, Exatas, Saude).
  ->	Tabela: Listando as materias com as maiores e menores médias de avaliação.
  ->	Dados Gerais: Numeros como "Total de Respostas Recebidas" e "Media Geral de Satisfação".
  
Relatório 2: Análise de Desempenho Individual (Visão do Professor/Coordenador)

-> O que mostra? Um detalhamento sobre um professor ou uma materia especifica.
-> Como?
  -> Gráfico de Linha: Mostra a evolução das notas de um professor ao longo de varios semestres (2024.1, 2024.2, 2025.1...).
  -> Tabela Detalhada: Para uma materia, mostra a media de cada pergunta (ex: Didatica: 4.5/5, Material de Aula: 3.8/5).
  -> Comentários: Exibe uma lista com todos os comentarios anonimos feitos pelos alunos para aquela turma.
