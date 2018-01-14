import copy

import GlobalParameters as gp
from Jeu import Block
from Jeu import State
from Jeu import Piece


def copy_grid(grid):
    size = (len(grid), len(grid[0]))
    new_grid = list()
    for i in range(size[0]):
        new_grid += [list()]
        for j in range(size[1]):
            new_grid[i] += [copy.copy(grid[i][j])]
    return new_grid

def best_move(heuristic, weights, state):
        pieces = copy.copy(state["pieces"])
        scores = []
        compteur = 0

        for kind in pieces:
            for rotation in range(0, 4, 1):
                for move in range(-5, 7, 1):
                    play = {"choose": kind,
                            "rotate": rotation, "hor_move": move}
                    grid_tmp = State.State(copy_grid(state["grid"]))
                    grid_prec = State.State(copy_grid(state["grid"]))
                    p = Piece.Piece.factory(
                        kind, copy.copy(Piece.Piece.centers_init[kind]))
                    for _ in range(rotation):
                        p.rotate()
                    if(State.is_piece_accepted_abscisse(p, p.center[0] + p.block_control[0] + move)):
                        p.center[0] += move
                        r = grid_tmp.drop_piece(p, 0)
                        scores += [[play,
                                    evaluate_play(grid_prec, grid_tmp, play, weights, heuristic)]]

        scores.sort(key=lambda x: x[1], reverse=True)
        best = scores[0][1]
        best_plays = []
        for s in scores:
            if s[1] >= best:
                best_plays += [s]
        play_send = random.choice(best_plays)[0]
        return play_send

def evaluate_play(grid_prec, grid_next, action, weights, heuristic) :
        tot = 0
        for i,func in enumerate(heuristic):
            tot += weights[i]*func(grid_prec,grid_next,action)
        return tot

#Return the latest action's height
def height(g_prec, g_next, action) :
    pass

#(number of line last action)*(number of cells eliminated from the las piece)
def erosion(g_prec, g_next, action):
    pass

#number of empty/filled or filled/empty cells transition
def line_transition(g_prec, g_next, action):
    cpt = 0
    for j in range(gp.TAILLE_Y_LIMITE):
        for i in range(gp.TAILLE_X - 1) :
            if(g_next[i][j] == Block.Block.Empty and g_next[i+1][j] != Block.Block.Empty) or\
                (g_next[i][j] != Block.Block.Empty and g_next[i+1][j] == Block.Block.Empty) :
                cpt += 1
    return cpt

#number of empty/filled or filled/empty cells transition
def column_transition(g_prec, g_next, action):
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE-1) :
            if(g_next[i][j] == Block.Block.Empty and g_next[i][j+1] != Block.Block.Empty) or\
                (g_next[i][j] != Block.Block.Empty and g_next[i][j+1] == Block.Block.Empty) :
                cpt += 1
    return cpt

#number of holes
def holes(g_prec, g_next, action):
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE) :
            if(g_next[i][j] == Block.Block.Empty) :
                is_hole = True
                try :
                    if(g_next[i][j+1] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next[i][j-1] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next[i+1][j] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next[i-1][j] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                if is_hole :
                    cpt += 1
    return cpt

#number of wells :
def wells(g_prec, g_next, action) :
    cpt = 0
    #on compte les puits dans l'intérieur de la grille (attention dépassement indice)
    for i in range(1, gp.TAILLE_X-1) :
        for j in range(1, gp.TAILLE_Y_LIMITE) :
            #si on est à la source d'un puit
            if( g_next[i][j] == Block.Block.Empty and\
                g_next[i-1][j] != Block.Block.Empty and\
                g_next[i+1][j] != Block.Block.Empty and\
                g_next[i][j-1] != Block.Block.Empty and\
                g_next[i-1][j-1] != Block.Block.Empty and\
                g_next[i+1][j-1] != Block.Block.Empty) :
                #On trouve un puit ! On compte une case
                cpt += 1
                #puis on compte toute les autre en remontant le puit
                add = 2
                for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                    if g_next[i][k] == Block.Block.Empty and\
                        g_next[i-1][k] != Block.Block.Empty and\
                        g_next[i+1][k] != Block.Block.Empty :
                        cpt += add
                        add += 1
                    else :
                        break
                print("Puit en " + str(i) + " rapporte " + str(cpt))
                break


    #cas si le puit est tout à gauche
    for j in range(1, gp.TAILLE_Y_LIMITE) :
        if(g_next[0][j] == Block.Block.Empty and\
            g_next[0][j-1] != Block.Block.Empty and\
            g_next[1][j] != Block.Block.Empty and\
            g_next[1][j-1] != Block.Block.Empty) :
            #on détecte un puit, on compte un case
            cpt += 1
            #on remonte le puit
            add = 2
            for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                if g_next[0][k] == Block.Block.Empty and\
                    g_next[1][k] != Block.Block.Empty :
                    cpt += add
                    add += 1
                else :
                    break
            print("Puit en " + str(0) + " rapporte " + str(cpt))
            break

    #cas tout à droite
    for j in range(1, gp.TAILLE_Y_LIMITE) :
        if(g_next[gp.TAILLE_X-1][j] == Block.Block.Empty and\
            g_next[gp.TAILLE_X-1][j-1] != Block.Block.Empty and\
            g_next[gp.TAILLE_X-2][j] != Block.Block.Empty and\
            g_next[gp.TAILLE_X-2][j-1] != Block.Block.Empty) :
            #on détecte un puit, on compte un case
            cpt += 1
            #on remonte le puit
            add = 2
            for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                if g_next[gp.TAILLE_X-1][k] == Block.Block.Empty and\
                    g_next[gp.TAILLE_X-2][k] != Block.Block.Empty :
                    cpt += add
                    add += 1
                else :
                    break
            print("Puit en " + str(0) + " rapporte " + str(cpt))
            break

    #coin gauche bas
    if g_next[0][0] == Block.Block.Empty and\
        g_next[1][0] != Block.Block.Empty :
        cpt += 1
        add = 2
        for k in range(1, gp.TAILLE_Y_LIMITE) :
            if g_next[0][k] == Block.Block.Empty and\
                g_next[1][k] != Block.Block.Empty :
                    cpt += add
                    add += 2
            else :
                break
        print("Puit en " + str(0) + " rapporte " + str(cpt))

    #coin droite bas
    if g_next[gp.TAILLE_X-1][0] == Block.Block.Empty and\
        g_next[gp.TAILLE_X-2][0] != Block.Block.Empty :
        cpt += 1
        add = 2
        for k in range(1, gp.TAILLE_Y_LIMITE) :
            if g_next[gp.TAILLE_X-1][k] == Block.Block.Empty and\
                g_next[gp.TAILLE_X-2][k] != Block.Block.Empty :
                    cpt += add
                    add += 2
            else :
                break
        print("Puit en " + str(gp.TAILLE_X-1) + " rapporte " + str(cpt))

    return cpt
