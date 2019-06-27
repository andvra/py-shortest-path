import sys, pygame
import random
import math
import numpy as np
import operator
import pygame.freetype

def init_nodes(n, fig_shape):
    width = 400
    height = 400
    # 1 = circle
    # 2 = rectangle
    # 3 = random
    if fig_shape==1:
        return [(int(width/2+(width/2)*math.sin(2*math.pi*i/n)), int(height/2+(height/2)*math.cos(2*math.pi*i/n))) for i in range(n)]
    elif fig_shape==2:
        node_d = (width+height)*2/n
        nodes = []
        for i in range(n):
            tot_d = i*node_d
            pos_x = 0
            if tot_d<width:
                pos_x=tot_d
            elif tot_d<width+height:
                pos_x=width
            elif tot_d<2*width+height:
                pos_x=2*width+height-tot_d
            pos_y = 0
            if tot_d<width:
                pos_y=0
            elif tot_d<width+height:
                pos_y=tot_d-height
            elif tot_d<2*width+height:
                pos_y=height
            else:
                pos_y=height-(tot_d-2*width-height)
            pos_x=int(pos_x)
            pos_y=int(pos_y)
            nodes.append((pos_x,pos_y))
        return nodes
    else:
        return [(random.randint(0,width), random.randint(0,height)) for _ in range(n)]

def init_population(no_nodes, pop_size):
    return [random.sample(range(no_nodes), no_nodes) for _ in range(pop_size)]

def path_length(path):
    d = sum(list(map(lambda x: math.hypot(x[0][0]-x[1][0], x[0][1]-x[1][1]), path)))
    return d

def get_path_for_individual(nodes, individual):
    merged = zip(individual, individual[1:]+[individual[0]])
    path = list(map(lambda x: (nodes[x[0]], nodes[x[1]]), merged))
    return path

def order_by_fitness(nodes, population):
    paths = []
    ds = []
    for individual in population:
        path = get_path_for_individual(nodes, individual)
        d = path_length(path)
        paths.append(path)
        ds.append(d)
    idx = np.argsort(ds)
    best_paths = [paths[i] for i in idx]
    best_ds = [ds[i] for i in idx]
    best_individuals = [population[i] for i in idx]
    return best_individuals, best_paths, best_ds

def select_parents(population):
    pop_size = len(population)
    by_fitness = 0.3
    by_chance = 0.1
    no_fitness = int(by_fitness*pop_size)
    no_chance = int(by_chance*pop_size)
    # Pick some samples by fitness ranking, and some by random
    parents = population[:no_fitness]+random.sample(population[no_fitness:], no_chance)
    return parents

def crossover(parents, no_children):
    new_population=[]
    no_genes = len(parents[0])
    for i in range(no_children):
        p1, p2 = random.sample(parents, 2)
        start = random.randint(0,no_genes-1)
        l = random.randint(1,no_genes-start)
        added = set()
        child = [math.inf for _ in range(no_genes)]
        child[start:start+l]= p1[start:start+l]
        for i in range(start, start+l):
            child[i] = p1[i]
            added.add(p1[i])
        for i in range(no_genes):
            if (child[i]== math.inf) and not p2[i] in added:
                child[i]=p2[i]
                added.add(p2[i])
        # Make sure the nodes not yet in child are added
        remaining = list(set(p1)-added)
        random.shuffle(remaining)
        for i in range(no_genes):
            if child[i]==math.inf:
                child[i]=remaining.pop()

        new_population.append(child)
    return new_population

def mutate(population,p_mutation):
    for individual in population:
        if random.random()<p_mutation:
            r1 = random.randint(0,len(individual)-1)
            r2 = random.randint(0,len(individual)-1)
            v1 = individual[r1]
            individual[r1]=individual[r2]
            individual[r2]=v1
    return population

def breed(population,p_mutation):
    parents = select_parents(population)
    new_population = crossover(parents, len(population))
    new_population = mutate(new_population, p_mutation)
    return new_population

def draw_nodes(nodes, offset=(0,0)):
    col_diff=255//len(nodes)
    for i, node in enumerate(nodes):
        col = (255-col_diff*i,128+0.5*col_diff*i,255)
        pos = tuple(map(operator.add, node, offset))
        s = 5
        pygame.draw.circle(screen, col, pos, s)

def draw_edges(path, offset=(0,0)):
    for es, ee in path:
        start = tuple(map(operator.add,es,offset))
        end = tuple(map(operator.add,ee,offset))
        pygame.draw.line(screen, col_line, start, end, 5)

def print_usage():
    print("Usage:")
    print("   -s=[n] (optional)")
    print("       1 = circle, 2 = square, 3 = random")
    print("   -n=[n] (optional)")
    print("       Number of nodes to use")
    sys.exit()

def parse_arguments(argv):
    fig_shape = 1
    no_nodes = 50
    use_gfx = True
    for arg in argv[1:]:
        if len(arg)>0 and arg[0]=='-':
            if arg.count("=")==0:
                k = arg[1:]
            else:
                k, v = arg[1:].split('=')
            if k=="s":
                fig_shape=int(v)
            elif k=="n":
                no_nodes = int(v)
            elif k=="c":
                use_gfx = False
            else:
                print_usage()
        else:
            print_usage()
    return no_nodes, fig_shape, use_gfx

if __name__ == "__main__":
    p_mutation=0.5
    no_nodes, fig_shape, use_gfx = parse_arguments(sys.argv)
    if use_gfx==False:
        print("Using CLI")
    pop_size = no_nodes*15
    nodes = init_nodes(no_nodes, fig_shape)
    population = init_population(no_nodes, pop_size)
    population, best_paths, best_ds = order_by_fitness(nodes, population)
    best_path = best_paths[0]
    best_d = best_ds[0]
    alltime_best_path = best_path
    alltime_best_d = best_d
    alltime_best_gen = 1
    pygame.init()
    clk = pygame.time.Clock()
    if use_gfx:
        size = width, height = 1400, 600
        col_bg = (50,50,50)
        col_node = (150,150,150)
        col_line = (100,100,100)
        col_txt = (200,200,50)
        font = pygame.freetype.SysFont("Arial", 24)
        screen = pygame.display.set_mode(size)
        txt_best_d, _ = font.render("Shortest: {:.1f}".format(alltime_best_d),col_txt)
        txt_best_gen, _ = font.render("Generation: {}".format(alltime_best_gen),col_txt)
        txt_fps, _ = font.render("FPS")
        txt_p_mutation, _=font.render("")

    running = True
    cur_gen = 1
    last_update = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    p_mutation = np.minimum(1,p_mutation+0.05)
                if event.key == pygame.K_o:
                    p_mutation = np.maximum(0,p_mutation-0.05)
        if use_gfx:
            screen.fill(col_bg)
            screen.blit(txt_fps, (1100,50))
            screen.blit(txt_best_d, (1100,100))
            screen.blit(txt_best_gen, (1100,150))
            screen.blit(txt_p_mutation, (1100,200))
            draw_edges(best_path,(100,100))
            draw_nodes(nodes,(100,100))
            draw_edges(alltime_best_path, (600,100))
            draw_nodes(nodes,(600,100))
        clk.tick()
        if last_update+500<pygame.time.get_ticks():
            fps = clk.get_fps()
            last_update=pygame.time.get_ticks()
            if use_gfx:
                txt_fps, _ = font.render("FPS: {:.1f}".format(fps), col_txt)
                txt_best_d, _ = font.render("Shortest: {:.1f}".format(alltime_best_d),col_txt)
                txt_best_gen, _ = font.render("Generation: {}/{}".format(alltime_best_gen,cur_gen),col_txt)
                txt_p_mutation, _ = font.render("P(mutation): {:.2f}. Keys:o/p".format(p_mutation),col_txt)
            else:
                print("Shortest: {:.1f} Generation: {}/{} FPS: {:.1f}".format(alltime_best_d,alltime_best_gen,cur_gen,fps),end="\r")
        population = breed(population,p_mutation)
        population, best_paths, best_ds = order_by_fitness(nodes, population)
        best_path = best_paths[0]
        best_d = best_ds[0]
        cur_gen += 1
        if best_d<alltime_best_d:
            alltime_best_d=best_d
            alltime_best_path=best_path
            alltime_best_gen = cur_gen
        if use_gfx:
            pygame.display.flip()

    pygame.quit()