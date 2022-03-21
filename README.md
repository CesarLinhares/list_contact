# list_contact
 Projeto feito com FastAPI
___
### Ajustes
* Singleton connection já basta, não é necessário uma outra função para conectar. E a função de conexão não precisa de parâmetros, pode ser fixo da função.


* Interface do repositório já está implementando os métodos, e ela deve só definí-los


* Arrumar o soft delete, que não atualiza as informações novas quando registra de novo
Repositório


* Fazer a implementação dos métodos da interface


* Não ficar convertendo JSON/dicionário, trabalhar direto com dicionário


* Na pasta de repositório as interfaces são implementadas no próprio repositório em uma classe, e as classes filhas vão herdar desse único pai no repositório.
Serviço


* Fazer as funcionalidades do serviço em um único arquivo.

---

| Cesar            | João            |
|:----------------:|:---------------:|
| Cadastrar        | Editar          |
| Buscar por letra | Listagens       |
| Detalhe          | Excluir         |
| Contagem         | Contagem        |
| Sigleton redis   | Singleton Mongo |