// File: louvain.cpp
// -- community detection source file
//-----------------------------------------------------------------------------
// Community detection
// Based on the article "Fast unfolding of community hierarchies in large networks"
// Copyright (C) 2008 V. Blondel, J.-L. Guillaume, R. Lambiotte, E. Lefebvre
//
// This file is part of Louvain algorithm.
// 
// Louvain algorithm is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// Louvain algorithm is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with Louvain algorithm.  If not, see <http://www.gnu.org/licenses/>.
//-----------------------------------------------------------------------------
// Author   : E. Lefebvre, adapted by J.-L. Guillaume
// Email    : jean-loup.guillaume@lip6.fr
// Location : Paris, France
// Time	    : February 2008
//-----------------------------------------------------------------------------
// see readme.txt for more details

#include "louvain.h"

using namespace std;


Louvain::Louvain(int nbp, long double epsq, Quality* q) {
  qual = q;

  neigh_weight.resize(qual->size,-1);
  neigh_pos.resize(qual->size);
  neigh_last = 0;


  neigh_weight_h.resize(qual->size,-1);
  neigh_pos_h.resize(qual->size);
  neigh_last_h = 0;
  
  nb_pass = nbp;
  eps_impr = epsq;
}

void
Louvain::init_partition(char * filename) {
  cerr << "Don't use this!" << endl;
  /*
  ifstream finput;
  finput.open(filename,fstream::in);

  // read partition
  while (!finput.eof()) {
    int node, comm;
    finput >> node >> comm;
    
    if (finput) {
      int old_comm = qual->n2c[node];
      neigh_comm(node);

      qual->remove(node, old_comm, neigh_weight[old_comm]);
      
      int i=0;
      for (i=0 ; i<neigh_last ; i++) {
	int best_comm = neigh_pos[i];
	long double best_nblinks = neigh_weight[neigh_pos[i]];
	if (best_comm==comm) {
	  qual->insert(node, best_comm, best_nblinks);
	  break;
	}
      }
      if (i==neigh_last)
	qual->insert(node, comm, 0);
    }
  }
  finput.close();
  */
}

void
Louvain::neigh_comm(int node) {
  for (int i=0 ; i<neigh_last ; i++)
    neigh_weight[neigh_pos[i]]=-1;
  
  neigh_last = 0;

  pair<vector<int>::iterator, vector<long double>::iterator> p = (qual->g).neighbors(node);
  int deg = (qual->g).nb_neighbors(node);

  neigh_pos[0] = qual->n2c[node];
  neigh_weight[neigh_pos[0]] = 0;
  neigh_last = 1;

  for (int i=0 ; i<deg ; i++) {
    int neigh  = *(p.first+i);
    int neigh_comm = qual->n2c[neigh];
    long double neigh_w = ((qual->g).weights.size()==0)?1.0L:*(p.second+i);
    
    if (neigh!=node) {
      if (neigh_weight[neigh_comm]==-1) {
	neigh_weight[neigh_comm] = 0.0L;
	neigh_pos[neigh_last++] = neigh_comm;
      }
      neigh_weight[neigh_comm] += neigh_w;
    }
  }
}

//////////////////////////////////////
void
Louvain::neigh_comm_h(int node) {
	//set vector to -1s
  for (int i=0 ; i<neigh_last_h ; i++)
    neigh_weight_h[neigh_pos_h[i]]=-1;
  
  neigh_last_h = 0;

  pair<vector<int>::iterator, vector<long double>::iterator> p = (qual->h).neighbors(node); //neighbours of target node in h
  int deg = (qual->h).nb_neighbors(node); //number of neighbours of target node in h

  neigh_pos_h[0] = qual->n2c[node]; //community of target node
  neigh_weight_h[neigh_pos_h[0]] = 0;
  neigh_last_h = 1;

  for (int i=0 ; i<deg ; i++) {
    int neigh  = *(p.first+i); //neighbour node
    int neigh_comm = qual->n2c[neigh]; //neighbour's community
    long double neigh_w = ((qual->h).weights.size()==0)?1.0L:*(p.second+i);
    
    if (neigh!=node) { //don't count self loops
      if (neigh_weight_h[neigh_comm]==-1) {//first link to community 'neigh_comm'
	neigh_weight_h[neigh_comm] = 0.0L;
	neigh_pos_h[neigh_last_h++] = neigh_comm;
      }
      neigh_weight_h[neigh_comm] += neigh_w;
    }
  }
  //neigh last = number of communities target node is attached to
  //neigh_pos = communities node is attached to
  //neigh_weight = weight of links between target node and community: neigh_weight[node_comm] = \sum_{j in C} A_nj
}
///////////////////////////////////////////////

void
Louvain::partition2graph() {
  vector<int> renumber(qual->size, -1);
  for (int node=0 ; node<qual->size ; node++) {
    renumber[qual->n2c[node]]++;
  }

  int end=0;
  for (int i=0 ; i< qual->size ; i++)
    if (renumber[i]!=-1)
      renumber[i]=end++;

  for (int i=0 ; i< qual->size ; i++) {
    pair<vector<int>::iterator, vector<long double>::iterator> p = (qual->g).neighbors(i);

    int deg = (qual->g).nb_neighbors(i);
    for (int j=0 ; j<deg ; j++) {
      int neigh = *(p.first+j);
      cout << renumber[qual->n2c[i]] << " " << renumber[qual->n2c[neigh]] << endl;
    }
  }
}

void
Louvain::display_partition() {
  vector<int> renumber(qual->size, -1);
  for (int node=0 ; node < qual->size ; node++) {
    renumber[qual->n2c[node]]++;
  }

  int end=0;
  for (int i=0 ; i < qual->size ; i++)
    if (renumber[i]!=-1)
      renumber[i] = end++;

  for (int i=0 ; i < qual->size ; i++)
    cout << i << " " << renumber[qual->n2c[i]] << endl;
}

Graph
Louvain::partition2graph_binary(bool gtype) {
  // Renumber communities
  vector<int> renumber(qual->size, -1);
  for (int node=0 ; node < qual->size ; node++)
    renumber[qual->n2c[node]]++;

  int last=0;
  for (int i=0 ; i < qual->size ; i++) {
    if (renumber[i]!=-1)
      renumber[i] = last++;
  }
  
  // Compute communities
  vector<vector<int> > comm_nodes(last);
  vector<int> comm_weight(last, 0);
  
  for (int node = 0 ; node < (qual->size) ; node++) {
    comm_nodes[renumber[qual->n2c[node]]].push_back(node);
    if( gtype ){
		comm_weight[renumber[qual->n2c[node]]] += (qual->g).nodes_w[node];
	} else {
		comm_weight[renumber[qual->n2c[node]]] += (qual->h).nodes_w[node];
	}
  }

  // Compute weighted graph
  Graph g2;
  int nbc = comm_nodes.size();

  g2.nb_nodes = comm_nodes.size();
  g2.degrees.resize(nbc);
  g2.nodes_w.resize(nbc);
  
  for (int comm=0 ; comm<nbc ; comm++) {
    map<int,long double> m;
    map<int,long double>::iterator it;

    int size_c = comm_nodes[comm].size();

    g2.assign_weight(comm, comm_weight[comm]);

    for (int node=0 ; node<size_c ; node++) {
      pair<vector<int>::iterator, vector<long double>::iterator> p;
      int deg;
      if( gtype ){
		p = (qual->g).neighbors(comm_nodes[comm][node]);
		deg = (qual->g).nb_neighbors(comm_nodes[comm][node]);
	  } else {
		p = (qual->h).neighbors(comm_nodes[comm][node]);
		deg = (qual->h).nb_neighbors(comm_nodes[comm][node]);
	  }
      for (int i=0 ; i<deg ; i++) {
	int neigh = *(p.first+i);
	int neigh_comm = renumber[qual->n2c[neigh]];
	long double neigh_weight;
	if( gtype ){
		neigh_weight = ((qual->g).weights.size()==0)?1.0L:*(p.second+i);
	} else {
		neigh_weight = ((qual->h).weights.size()==0)?1.0L:*(p.second+i);
	}

	it = m.find(neigh_comm);
	if (it==m.end())
	  m.insert(make_pair(neigh_comm, neigh_weight));
	else
	  it->second += neigh_weight;
      }
    }

    g2.degrees[comm] = (comm==0)?m.size():g2.degrees[comm-1]+m.size();
    g2.nb_links += m.size();

    for (it = m.begin() ; it!=m.end() ; it++) {
      g2.total_weight += it->second;
      g2.links.push_back(it->first);
      g2.weights.push_back(it->second);
    }
  }

  return g2;
}


bool
Louvain::one_level() {
  bool improvement=false ;
  int nb_moves;
  int nb_pass_done = 0;
  long double new_qual = qual->quality();
  long double cur_qual = new_qual;

  vector<int> random_order(qual->size);
  for (int i=0 ; i < qual->size ; i++)
    random_order[i]=i;
  for (int i=0 ; i < qual->size-1 ; i++) {
    int rand_pos = rand()%(qual->size-i)+i;
    int tmp = random_order[i];
    random_order[i] = random_order[rand_pos];
    random_order[rand_pos] = tmp;
  }
  // repeat while 
  //   there is an improvement of quality
  //   or there is an improvement of quality greater than a given epsilon 
  //   or a predefined number of pass have been done
  do {
    cur_qual = new_qual;
    nb_moves = 0;
    nb_pass_done++;

    // for each node: remove the node from its community and insert it in the best community
    for (int node_tmp = 0 ; node_tmp < qual->size ; node_tmp++) {

      int node = random_order[node_tmp];
      int node_comm = qual->n2c[node];
      long double w_degree = (qual->g).weighted_degree(node);

      // computation of all neighboring communities of current node
      neigh_comm(node);
      neigh_comm_h(node);
	  /*cerr << "node " << node << endl;
      for(int i=0; i<neigh_last_h; i++){
		  cout << "h " << i << " " << neigh_pos_h[i] << " " << neigh_weight_h[neigh_pos_h[i]] << endl;
	  }
	  for(int i=0; i<neigh_last; i++){
		  cout << "a " << i << " " << neigh_pos[i] << " " << neigh_weight[neigh_pos[i]] << endl;
	  }*/
	  
      // remove node from its current community
      qual->remove(node, node_comm, neigh_weight[node_comm], neigh_weight_h[node_comm]);
      // compute the nearest community for node
      // default choice for future insertion is the former community
      int best_comm = node_comm;
      long double best_nblinks  = 0.0L;
      long double best_nblinks_h  = 0.0L;
      long double best_increase = 0.0L;
      for (int i=0 ; i<neigh_last ; i++) {
	if( (qual->name) == "UserNull" ){
		w_degree = neigh_weight_h[neigh_pos[i]];
	}
	long double increase = qual->gain(node, neigh_pos[i], neigh_weight[neigh_pos[i]], w_degree);
	//cerr << "node " << node << " " << node_comm << " np " << neigh_pos[i] << " " << neigh_weight[neigh_pos[i]] << " " << w_degree << 
	//" increase " << increase << endl;
	if (increase>best_increase) {
	  best_comm = neigh_pos[i];
	  best_nblinks = neigh_weight[neigh_pos[i]];
	  best_nblinks_h = neigh_weight_h[neigh_pos[i]];
	  //cerr << "node " << node << " best_comm " << best_comm << " :: " << " g " << best_nblinks << " h " << best_nblinks_h << endl;
	  best_increase = increase;
	}
      }
	  //cerr << node << " in " << best_comm << endl;
      // insert node in the nearest community
      //cerr << "node " << node << "into" << best_comm << " " << best_nblinks << " " << best_nblinks_h << endl;
      
      qual->insert(node, best_comm, best_nblinks, best_nblinks_h);
      if (best_comm!=node_comm)
	nb_moves++;
    }

    new_qual = qual->quality();
    
    if (nb_moves>0)
      improvement=true;
    
    //break;

  } while (nb_moves>0 && new_qual-cur_qual > eps_impr);
  //cerr << "new_qual " << new_qual << endl;

  return improvement;
}
