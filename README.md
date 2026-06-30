# Logitech MX Remapper & Macro Autoclicker

Utilitário leve em Python para remapear teclas/botões do mouse **Logitech MX Master 3** e do teclado **MX Mechanical**, configurar macros para manter o botão esquerdo do mouse pressionado (toggle hold) e exibir um indicador visual (tooltip) moderno, transparente e "click-through" (que não bloqueia cliques) na tela do Windows.

## Recursos
- **Remapeamento Global de Teclas:** Intercepta entradas de teclado (otimizado para o MX Mechanical) e as remapeia para outros cliques do mouse, rolagem ou atalhos.
- **Mapeamento de Botões do Mouse:** Remapeia botões padrão do mouse (clique esquerdo, direito, clique do meio e botões laterais Voltar/Avançar `XButton1`/`XButton2`).
- **Macro de Segurar o Clique Esquerdo:** Alterna o estado de segurar o botão esquerdo do mouse (clique contínuo pressionado) através de uma tecla configurável.
- **Autoclicker:** Clica repetidamente em um intervalo de milissegundos configurável.
- **HUD/Tooltip elegante na tela:** Um indicador visual sem bordas, semissensível e transparente que flutua na tela mostrando se o Autoclicker ou o Macro de segurar clique estão ativos. Ele é configurado com a API do Windows para ser totalmente "click-through", ou seja, você pode clicar através dele sem que ele atrapalhe seu jogo ou trabalho.
- **Configuração JSON Simples:** Arquivo `config.json` para ajustar atalhos, velocidades, cores, fontes, transparência e posições do tooltip de forma fácil.

---

## Guia de Configuração com Logitech Options+

Para remapear botões proprietários do **MX Master 3** (como o botão de Gesto ou a roda do polegar - Thumb Wheel) ou teclas especiais do **MX Mechanical**:
1. Abra o software **Logi Options+**.
2. Selecione seu dispositivo.
3. Mapeie o botão desejado (ex: o botão de Gesto ou clique do polegar) para enviar um **Atalho de Teclado** não utilizado no dia a dia, como `F13` até `F24`, ou combinações complexas como `Ctrl+Alt+Shift+F12`.
4. No arquivo `config.json` do nosso projeto, associe essa mesma tecla (`"f13"`, `"f24"`, etc.) à ação ou macro que deseja executar.

Os botões de Voltar e Avançar laterais (`X1` e `X2` no mouse) são botões de mouse padrão do Windows e serão detectados nativamente pelo programa sem precisar de reconfiguração no Logi Options+.

---

## Estrutura de Configuração (`config.json`)

Você pode configurar todos os comportamentos no arquivo `config.json` na raiz do projeto:

```json
{
  "autoclicker": {
    "toggle_key": "f6",
    "interval_ms": 100,
    "target_button": "left"
  },
  "macros": {
    "lbutton_hold_toggle_key": "f7"
  },
  "remappings": {
    "keys": {
      "f13": "left_click",
      "f14": "scroll_up",
      "f15": "scroll_down"
    },
    "mouse": {
      "x2": "ctrl+c"
    }
  },
  "overlay": {
    "enabled": true,
    "position": "top_center",
    "offset_x": 0,
    "offset_y": 20,
    "opacity": 0.85,
    "font_family": "Segoe UI",
    "font_size": 10,
    "bg_color": "#1e1e2e",
    "text_color": "#cdd6f4",
    "active_color": "#a6e3a1"
  }
}
```

### Parâmetros Importantes:
- **`autoclicker.toggle_key`**: Tecla para ligar/desligar o autoclicker.
- **`macros.lbutton_hold_toggle_key`**: Tecla que ativa/desativa o estado de "segurar" o botão esquerdo do mouse.
- **`remappings.keys`**: Dicionário de remapeamento de teclas do teclado para ações. Ações suportadas: `"left_click"`, `"right_click"`, `"middle_click"`, `"scroll_up"`, `"scroll_down"` ou qualquer caractere/atalho.
- **`remappings.mouse`**: Dicionário de remapeamento de botões do mouse (`"x1"`, `"x2"`, `"middle"`) para atalhos do teclado.
- **`overlay.position`**: Onde o tooltip ficará posicionado (`"top_left"`, `"top_center"`, `"top_right"`, `"bottom_left"`, `"bottom_center"`, `"bottom_right"`, ou uma string com coordenadas `"X,Y"` ex: `"500,300"`).

---

## Requisitos e Instalação

1. Certifique-se de ter o **Python 3.10+** instalado no Windows.
2. Instale as dependências executando o prompt de comando na raiz do projeto:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o utilitário usando o alias criado:
   ```bash
   autoclicker
   ```
   *(Ou se preferir, pode rodar o comando manual: `python src/main.py`)*
4. Pressione as teclas configuradas para ativar as funções e veja o tooltip atualizar seu estado na tela em tempo real!
5. Para encerrar o utilitário, você pode focar na janela do terminal, digitar **`q`** e pressionar **Enter** (ou fechar o tooltip/pressionar Ctrl+C).