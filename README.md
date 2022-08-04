# Jogo da velha (servidor, clientes)

Projeto final da disciplina de protocolos de aplicação do CST Redes de Computadores do IPFB

Código fonte para servidor e clientes multiplayer do jogo da velha.

Para rodar aplicação:

  1. Python 3 instalado;
  1. Verificar ip addr para servidor e porta no arquivo do servidor;
  3. Iniciar servidor: python3 jogo-da-velha-server.py;
  4. Clicar no botão "Start" na janela do servidor;
  5. Verificar ip addr para servidor no arquivo do cliente;
  6. Iniciar clientes: python3 jogo-da-velha-cliente.py
  7. Inserivr nome do jogador e clicar em "entrar";
  8. O jogo inicia quando dois jogadores estiverem conectados.

## protocolo de aplicação proprietário

* o servidor gerencia a conexão dos jogadores 1 e 2 colocando as demais conexões em espera
* O servidor faz o encaminhamento dos dados de um jogador para o outro.
* A aplicação fica distribuída entre os dois jogadores, havendo apenas a troca de informações dos jogadores através do servidor, que encaminha a coordenada da jogada de um jogador ao outro.

  1. cliente ao se conectar envia o nome fornecido ao servidor
  1. servidor responde com “welcome” e numero do jogador “1” ou “2”
  1. quando o segundo jogador se conecta, enviando seu nome, o servidor envia o nome e sinal (x ou 0) do segundo jogador 2 para jogador 1, bem como o nome e sinal do jogador 1 para jogador 2.
  1. $opponent_name$nomeJogador1symbolX
  1. $opponent_name$nomeJogador2symbolO
  1. jogador1 envia sua jogada ao servidor no formato $xy$0$0
  1. jogador2 envia sua jogada ao servidor no formato $xy$0$0

* São enviadas as coordenas $xy, sendo x correspondente ao primeiro valor $0, e sendo y correspondente ao segundo $0 para a posição 0,0 do grid. observe que o grid varia de 0,0 a 2,2 conforme posição do tabuleiro.

