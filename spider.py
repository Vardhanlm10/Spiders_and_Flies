from game import Game, Directions, Actions, GameStateData, GameState, GameDynamics

def manhattanDistance(xy1, xy2):
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def HorizonatalDistance(xy1, xy2):
    return abs(xy1[0] - xy2[0])

class Agents:
    def getNextAction(self,gameState):
        pass
    
class BasePolicy(Agents):
    def getNextAction(self,gameState):
        spiderPos = gameState.getSpidersPositions().copy()
        fliesPos = gameState.getFliesPositions().copy()
        minDistances = []
        # Calculating the manhattan distance from all the possible next states to all the flies 
        for spider in spiderPos:
            legalActions = gameState.getLegalActions(spider)
            distances = [(dir,manhattanDistance(vec,fvec), HorizonatalDistance(vec,fvec)) for dir,vec in legalActions for fvec in fliesPos]
            # Find the minimum distance
            minDistances.append(min(distances, key=lambda x: (x[1], x[2])))
        return [dir for dir,dist,h_dist in minDistances]


class OrdinaryRollout(Agents):
    # u = min[g(x,u1,u2) + J(f(x,u1,u2))] 
    def getNextAction(self,gameState):
        spiderPos = gameState.getSpidersPositions().copy()
        fliesPos = gameState.getFliesPositions().copy()
        #print(f"Spider position - {spiderPos}")
        #print(f"Flies Pos - {fliesPos}")

        legalActions = [gameState.getLegalActions(spider) for spider in spiderPos]
        # Generating all the possible outcomes
        possibleMoves = []
        for y in legalActions:
            if not possibleMoves:
                possibleMoves = [[z] for z in y]
            else:
                possibleMoves = [x+[z] for x in possibleMoves for z in y] 
        
        #print(possibleMoves)
        # u = min[g(x,u1,u2) + J(f(x,u1,u2))] = min[g(x,u1,u2)] + min[J(f(x,u1,u2))]
        costs = []
        for moves in possibleMoves:
            sim_gameState = GameState(gameState.data.gridSize, {'S': spiderPos.copy(), 'F': fliesPos.copy()})
            spiderPos_new = [move[0] for move in moves]
            sim_gameState.generateSucssorState(0, spiderPos_new)
            sim_spiderPos = sim_gameState.getSpidersPositions()
            sim_fliesPos = sim_gameState.getFliesPositions()
          
          # Create a simulation game with graphics disabled
            sim_game = Game(
                gameState.data.gridSize, 
                sim_spiderPos, 
                sim_fliesPos, 
                i=2, 
                speed=0.001, 
                graphics=False  # Disable graphics for simulation
            )
            
            # Run the simulation with base policy
            steps = sim_game.run(BasePolicy())
            costs.append([moves, steps])

        #print(costs)
        minimization = min(costs,key=lambda x: x[1])
        #print(minimization)

        #print(f"cost per move {minimization}")
        directions = [dir[0] for dir in minimization[0]]
        #print(directions)
        return directions
        

   

class MultiAgentRollout(Agents):
    
    def getNextAction(self,gameState):
        spiderPos = gameState.getSpidersPositions().copy()
        fliesPos = gameState.getFliesPositions().copy()

        legalActions = [gameState.getLegalActions(spider) for spider in spiderPos]
        # print(legalActions)
        final_actions = []

        base_policy_actions = BasePolicy().getNextAction(gameState)
        # print(base_policy_actions)
        
        for i in range(len(spiderPos)):
            possible_actions = legalActions[i]
            action_cost = []
            for action in possible_actions:
                all_actions = []
                for j in range(i):  # Copy actions before index i
                    all_actions.append(final_actions[j])

                all_actions.append(action[0])  # Insert the new action at index i

                for j in range(i+1, len(spiderPos)):  # Copy actions after index i
                    all_actions.append(base_policy_actions[j])
                
                # print(f"all_actions {all_actions}")
                sim_gameState = GameState(gameState.data.gridSize, {'S': spiderPos.copy(), 'F': fliesPos.copy()})
                sim_gameState.generateSucssorState(0, all_actions)
                sim_spiderPos = sim_gameState.getSpidersPositions()
                sim_fliesPos = sim_gameState.getFliesPositions()
                sim_game = Game(
                    gameState.data.gridSize, 
                    sim_spiderPos, 
                    sim_fliesPos, 
                    i=2, 
                    speed=0.001, 
                    graphics=False  # Disable graphics for simulation
                )
                
                # Run the simulation with base policy
                steps = sim_game.run(BasePolicy())
                action_cost.append([action, steps])
            final_actions.append(min(action_cost, key=lambda x: x[1])[0][0])

        

        return final_actions



    

