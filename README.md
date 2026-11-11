# Pátio de Operações — Computação Gráfica


**Alunos:** João Vicente Batista da Cunha e Nelice Gomes Araujo


## 1. Descrição da cena

A aplicação apresenta um pátio logístico tridimensional. Um carrinho de carga percorre o pátio, aproxima-se da área de operação e para quando o boneco de blocos sinaliza. O boneco levanta os braços para indicar a parada, movimenta um dos braços para indicar a mudança de percurso e dá alguns passos para liberar a passagem. Depois do sinal, o carrinho retoma o deslocamento, chega à doca e para. A caixa transportada é então deslocada para a plataforma de recebimento. Por fim, o carrinho retorna ao ponto inicial e o ciclo pode recomeçar.

A sincronização é programada por etapas de tempo, sem depender da taxa de quadros e sem exigir simulação física ou detecção de colisões.

## 2. Requisitos gráficos

O projeto implementa um subconjunto próprio e compacto da arquitetura de framework estudada no livro (grafo de cena, nós hierárquicos, câmera, malhas, shaders, materiais e renderer).

- Dois modelos tridimensionais reconhecíveis: veículo com carroceria, cabine, faróis, para-choques e rodas; personagem com cabeça, tronco, braços, antebraços, mãos, pernas e pés.
- Animação dos dois temas e interação temporal entre eles.
- Translação, rotação e escala nas partes dos modelos.
- Hierarquia de cena: grupos e objetos-filhos; os membros do boneco e as rodas acompanham os grupos-pais.
- Câmera em perspectiva controlada pelo teclado.
- Pausa e retomada sem fechar a janela.
- Textura de imagem aplicada ao piso, com coordenadas UV.
- Iluminação direcional, cálculo difuso e especular, materiais com cores e vetores normais por vértice.
- Shadow mapping: passagem de profundidade a partir da luz direcional, textura de profundidade em framebuffer e consulta com filtragem PCF na renderização principal.

## 3. Instalação

Recomendado: Python 3.10 ou superior e uma placa/driver com suporte a OpenGL 3.3 Core.

No terminal, dentro desta pasta:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

- Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
- Windows CMD: `.venv\Scripts\activate.bat`
- Linux/macOS: `source .venv/bin/activate`

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute:

```bash
python main.py
```

## 4. Controles

| Tecla | Ação |
|---|---|
| W / A / S / D | Mover a câmera para frente, esquerda, trás e direita |
| Q / E | Subir e descer a câmera |
| Setas | Alterar a orientação da câmera |
| Espaço | Pausar ou retomar a animação |
| R | Reiniciar o ciclo da animação |
| Esc | Encerrar a aplicação |

## 5. Organização dos arquivos

O projeto foi dividido por responsabilidade para que alterações em uma parte não exijam modificar todo o código:

```text
main.py                 Entrada da aplicação e loop principal
engine/                 Núcleo do motor de cena e renderização
  __init__.py           Exporta os componentes públicos do engine
  core.py               OpenGL, shaders, malhas, nós, câmera, luz e renderer
geometry/               Modelos geométricos reutilizáveis
  __init__.py           Exporta os construtores de geometria
  primitives.py         Cubo, cilindro e esfera
scene/                  Conteúdo e comportamento da cena
  __init__.py           Exporta a montagem e a animação
  builder.py            Cria o piso, carrinho, boneco e carga
  animation.py          Controla o roteiro temporal e os movimentos
assets/                 Recursos externos da aplicação
  textures/             Imagens usadas pelos materiais
    asphalt.png         Textura do piso
shaders/                Programas executados na GPU
  scene.vert            Vértices da renderização principal
  scene.frag            Cores, textura, iluminação e sombras
  depth.vert            Vértices da passagem do shadow mapping
  depth.frag            Fragmentos da passagem de profundidade
requirements.txt        Bibliotecas Python necessárias
README.md               Documentação, instalação e conceitos do projeto
```

### Arquivos Python

- `main.py`: inicia o Pygame, configura o contexto OpenGL, cria a cena, processa teclado/eventos e executa o loop de renderização.
- `engine/core.py`: implementa o núcleo técnico: `Geometry` para VBO/VAO, `ShaderProgram` para shaders, `Node`/`Group`/`Mesh`/`Scene` para o grafo hierárquico, `Camera`, `DirectionalLight`, `ShadowMap` e `Renderer`.
- `engine/__init__.py`: disponibiliza os componentes do engine para outros módulos por meio de imports simples, como `from engine import Camera`.
- `geometry/primitives.py`: gera os vértices, normais e UVs das geometrias de cubo, cilindro e esfera.
- `geometry/__init__.py`: reúne e exporta as geometrias primitivas.
- `scene/builder.py`: monta todos os objetos da cena e define a hierarquia do carrinho, do boneco, das rodas, dos braços, das pernas e da carga.
- `scene/animation.py`: calcula o caminho do carrinho, a caminhada do boneco, os movimentos dos braços e a transferência da carga ao longo do ciclo de 17 segundos.
- `scene/__init__.py`: disponibiliza `make_scene` e `update_animation` para o ponto de entrada.

### Shaders e recursos

- `shaders/scene.vert`: transforma os vértices usando as matrizes de modelo, câmera e projeção e envia normais, UVs e posição no espaço da luz.
- `shaders/scene.frag`: calcula a cor final usando material, textura, iluminação ambiente/difusa/especular e shadow mapping com PCF.
- `shaders/depth.vert`: transforma a geometria pelo espaço da luz para registrar profundidade.
- `shaders/depth.frag`: completa a passagem de profundidade usada pelo mapa de sombras.
- `assets/textures/asphalt.png`: imagem carregada como textura do piso.
- `requirements.txt`: lista `pygame`, `PyOpenGL`, `numpy` e `Pillow`, necessários para executar o projeto.

## 6. Conceitos técnicos para explicar na apresentação

### Pipeline e atributos de vértice

As geometrias são armazenadas em VBOs e associadas a um VAO. Cada vértice possui oito valores: posição (`aPosition`, 3 floats), normal (`aNormal`, 3 floats) e coordenada de textura (`aUV`, 2 floats). O vertex shader aplica as matrizes de modelo, visualização e projeção e envia posição global, normal, UV e posição no espaço da luz ao fragment shader.

### Transformações e hierarquia

Cada nó possui translação, rotação e escala. Sua matriz global é calculada pela multiplicação da matriz do pai pela matriz local. Assim, rodas, carroceria e membros do personagem herdam o movimento do respectivo grupo. A rotação das rodas e dos braços é atualizada em função do tempo da animação.

### Animação independente da taxa de quadros

O loop mede o tempo decorrido com `pygame.time.Clock().tick()`. A posição e ângulos dos elementos são calculados a partir de `sim_time`, e o tempo avança por `dt` apenas quando a animação não está pausada. Por isso, o deslocamento não é definido por uma quantidade fixa de pixels ou graus por quadro.

### Textura

A imagem `assets/textures/asphalt.png` é carregada em uma textura OpenGL. As coordenadas UV dos vértices são interpoladas e usadas pelo fragment shader para consultar a imagem por `sampler2D`.

### Iluminação e normais

A luz direcional possui uma direção e uma cor. O fragment shader calcula a contribuição ambiente, difusa (produto escalar entre normal e direção da luz) e especular. A normal do vértice é transformada pela inversa transposta da matriz de modelo para permanecer coerente com a transformação do objeto.

### Sombreamento de superfície x sombra projetada

O sombreamento é a variação de intensidade da cor sobre a própria superfície, calculada pela orientação da normal em relação à luz. A sombra projetada é diferente: o shadow mapping cria uma textura de profundidade vista pela luz. Na passagem principal, a posição do fragmento é comparada com a profundidade armazenada; quando outro ponto está mais próximo da luz, o fragmento recebe redução de iluminação. A amostragem PCF suaviza as bordas da sombra.

## 7. Sequência temporal da interação

O ciclo dura 17 segundos e se repete:

1. 0–3,7 s: carrinho aproxima-se; boneco sinaliza a aproximação.
2. 3,7–5,2 s: carrinho permanece parado; boneco levanta os braços para sinalizar parada.
3. 5,2–8,5 s: boneco indica a direção e desloca-se para liberar o caminho; carrinho segue o trajeto orientado.
4. 8,5–11 s: carrinho permanece na doca; a carga é transferida visualmente para a plataforma.
5. 11–17 s: carrinho retorna ao início; boneco conclui a orientação e o ciclo reinicia.

## 8. Contribuições individuais

Preencher antes da entrega, de acordo com o trabalho efetivamente realizado:

- Integrante 1: João Vicente Batista Da Cunha — [modelagem/animação/recursos implementados].
- Integrante 2: Nelice Gomes Araujo — [modelagem/animação/recursos implementados].

## 9. Declaração de uso de inteligência artificial

Ferramentas utilizadas: ChatGPT (OpenAI) e Gemini (Google).

Finalidade: apoio na estruturação da proposta, elaboração, limpeza e revisão de código Python/GLSL, organização da documentação e explicação dos conceitos gráficos.

Trechos apoiados: `main.py`, `engine.py`, shaders e este README. Os integrantes executaram, revisaram, compreenderam e adaptaram o projeto para a versão final antes da apresentação, conforme a orientação do enunciado.

## 10. Referências

STEMKOSKI, Lee; PASCALE, Michael. *Developing Graphics Frameworks with Python and OpenGL*. 1. ed. Boca Raton: CRC Press, 2022. DOI: https://doi.org/10.1201/9781003181378.

Enunciado da disciplina: *Trabalho Prático — Computação Gráfica*, 2026/02.
