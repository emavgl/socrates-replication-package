# Bot 

A Bot has one or more **Behaviours**. A *Behaviour* encode the decision strategy used to choose the solidity function to call and its parameters.

Initially, a bot has no associated *behaviours*. To add a new behaviour you have to call the method `addBehaviour(name: string)` specifying the name of one of the available behaviours (`overflow`, `random`, `boundary`).

```typescript
let bot = new Bot(target, account, context);
bot.addBehaviour("overflow")
bot.addBehaviour("random")
bot.addBehaviour("boundary")
```

The object *Bot* has a function called `performAction` which randomly activates a single *behaviour* from the list of added *behaviours*. The selected behaviour is then used to select the function and the parameters and perform a new transaction.

```typescript
public async performAction() : Promise<any> {
    let selectedBehaviour: Behaviour =  RandomValueGenerator.getRandomElement(this._behaviours);
    return await selectedBehaviour.performAction();
}
```