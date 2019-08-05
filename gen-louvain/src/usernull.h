// File: modularity.h
// -- quality functions (for Modularity criterion) header file
//-----------------------------------------------------------------------------
// Community detection
// Based on the article "Fast unfolding of community hierarchies in large networks"
// Copyright (C) 2008 V. Blondel, J.-L. Guillaume, R. Lambiotte, E. Lefebvre
//
// And based on the article
// Copyright (C) 2013 R. Campigotto, P. Conde Céspedes, J.-L. Guillaume
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
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with Louvain algorithm.  If not, see <http://www.gnu.org/licenses/>.
//-----------------------------------------------------------------------------
// Author   : E. Lefebvre, adapted by J.-L. Guillaume and R. Campigotto
// Email    : jean-loup.guillaume@lip6.fr
// Location : Paris, France
// Time	    : July 2013
//-----------------------------------------------------------------------------
// see README.txt for more details


#ifndef USERNULL_H
#define USERNULL_H

#include "quality.h"

using namespace std;


class UserNull: public Quality {
 public:

  vector<long double> in, tot; // used to compute the quality participation of each community

  UserNull(Graph & gr, Graph & hr);
  ~UserNull();

  inline void remove(int node, int comm, long double dnodecomm, long double dnodecomm_h);

  inline void insert(int node, int comm, long double dnodecomm, long double dnodecomm_h);

  inline long double gain(int node, int comm, long double dnodecomm, long double w_degree);

  long double quality();
};


inline void
UserNull::remove(int node, int comm, long double dnodecomm, long double dnodecomm_h) {
  assert(node>=0 && node<size);

  //cerr << "take " << node << " from " << comm << "::in" 
  //<< in[comm] << " - " << 2.0L*dnodecomm + g.nb_selfloops(node) << " ::tot "
  //<< tot[comm] << " - " << 2.0L*dnodecomm_h + h.nb_selfloops(node) << endl;

  in[comm]  -= 2.0L*dnodecomm + g.nb_selfloops(node);
  tot[comm] -= 2.0L*dnodecomm_h + h.nb_selfloops(node);
  
  n2c[node] = -1;
}

inline void
UserNull::insert(int node, int comm, long double dnodecomm, long double dnodecomm_h) {
  assert(node>=0 && node<size);
  //cerr << "add " << node << " to " << comm << "::in" 
  //<< in[comm] << " + " << 2.0L*dnodecomm + g.nb_selfloops(node) << " ::tot "
  //<< tot[comm] << " + " << 2.0L << "*" << dnodecomm_h << "+" << h.nb_selfloops(node) << endl;
  
  in[comm]  += 2.0L*dnodecomm + g.nb_selfloops(node);
  tot[comm] += 2.0L*dnodecomm_h + h.nb_selfloops(node);


  n2c[node] = comm;
}

inline long double
UserNull::gain(int node, int comm, long double dnc, long double degc) {
  assert(node>=0 && node<size);  
  //cerr << "comm " << comm << " dnc " << dnc << " degc " << degc << endl; 

  return (dnc - degc);
}


#endif // USERNULL_H
