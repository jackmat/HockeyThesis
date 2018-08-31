#include <Rcpp.h>
#include <assert.h>
using namespace Rcpp;

struct node {
  double qstar[3];
  double curr_value[3];
  double occ;
  double r_w;
  double r_g;
  std::vector<int> c_ids;
  std::vector<double> c_occs;
};

//find all children to a node given its id
std::map<int, node> fill_nodes(DataFrame states, int nr_of_states, IntegerVector s_ids,
                               NumericVector s_occ, NumericVector r_w, NumericVector r_g){
  IntegerVector node_ids = states["NodeId"];
  IntegerVector child_ids = states["ChildId"];
  NumericVector child_o = states["ChildOccurrence"];
  std::map<int, node> nodes;
  int current_index = 0;
  for(int s = 0; s < nr_of_states; s++){
    std::vector<int> c_ids;
    std::vector<double> c_occs;
    for(int i = current_index; i < node_ids.length(); i++){
      if(node_ids[i] == s_ids[s]){
        if(child_ids[i] != NA_INTEGER){
          c_ids.push_back(child_ids[i]);
          c_occs.push_back(child_o[i]);
        }
      }else{
        break;
      }
    }
    if(c_ids.size() == 0){
      current_index++;
    }else{
      current_index += c_ids.size();  
    }
    struct node n = {{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, s_occ[s], r_w[s], r_g[s], c_ids, c_occs};
    nodes.insert(std::pair <int, node> (s_ids[s], n));
  }
  return nodes;
}

//convert std::map to Rcpp::NumericMatrix
NumericMatrix convert_map_to_matrix(std::map<int, node> &nodes, int nr_of_states){
  NumericMatrix q(nr_of_states, 4);
  std::map<int, node>::iterator it;
  int i = 0;
  for(it = nodes.begin(); it != nodes.end(); it++){
    q(i, 0) = it->first;
    q(i, 1) = it->second.qstar[0];
    q(i, 2) = it->second.qstar[1];
    q(i, 3) = it->second.qstar[2];
    i++;
  }
  return q;
}

//calc contribution from children (old q_values)
// double calc_contribution(IntegerVector child_ids, NumericVector child_occs, std::map<int, node> &nodes){
//   double sub_value = 0.0;
//   for(int i = 0; i < child_ids.length(); i++){
//     node n = nodes.at(child_ids[i]);
//     sub_value += child_occs[i]*n.qstar;
//   }
//   return sub_value;
// }

// [[Rcpp::export]]
NumericMatrix value_iteration_f(DataFrame states, int max_iter, double c, int nr_of_states,
                                NumericVector r_w, NumericVector r_g, NumericVector s_occ, IntegerVector s_ids) {
  std::map<int, node> nodes = fill_nodes(states, nr_of_states, s_ids, s_occ, r_w, r_g);
  int iterations = 0;
  //expected_goals, probability_next_home_goal, probability_next_away_goal
  bool converged[3] = {false, false, false};
  double curr_values[3] = {0.0, 0.0, 0.0};
  double last_values[3] = {0.0, 0.0, 0.0};
  for(int i=0; i < max_iter; i++){
    iterations = i;
    for(int s=0; s < nr_of_states; s++){
      node n = nodes.at(s_ids[s]);
      //expected goals
      if(!converged[0]){
        //find children q and calc contribution
        double value = 0.0;
        double qstar = 0.0;
        for(int k = 0; k < n.c_ids.size(); k++){
          node child = nodes.at(n.c_ids[k]);
          double sub_value = n.c_occs[k]*child.curr_value[0];
          //choose child with highest contribution
          if (qstar <= sub_value){
            qstar = sub_value;
          }
          value += sub_value;
        }
        n.curr_value[0] = n.r_g + value/n.occ;
        n.qstar[0] = n.r_g + qstar/n.occ;
        nodes[s_ids[s]] = n;
        curr_values[0] += std::abs(n.curr_value[0]);
      }
      //probability_next_home_goal
      if(!converged[1]){
        //find children q and calc contribution
        double value = 0.0;
        double qstar = 0.0;
        for(int k = 0; k < n.c_ids.size(); k++){
          node child = nodes.at(n.c_ids[k]);
          double sub_value = 0.0;
          //is home goal?
          if (child.r_g > 0){
            sub_value = n.c_occs[k]*1.0;
          }
          //is away goal?
          else if(child.r_g < 0){
            sub_value = 0.0;
          }
          else{
            sub_value = n.c_occs[k]*child.curr_value[1];
          }
          if (qstar <= sub_value){
            qstar = sub_value; 
          }
          value += sub_value;
        }
        n.curr_value[1] = value/n.occ;
        n.qstar[1] = qstar/n.occ;
        nodes[s_ids[s]] = n;
        curr_values[1] += std::abs(n.curr_value[1]);
      }
      //probability_next_away_goal
      if(!converged[2]){
        //find children q and calc contribution
        double value = 0.0;
        double qstar = 0.0;
        for(int k = 0; k < n.c_ids.size(); k++){
          node child = nodes.at(n.c_ids[k]);
          double sub_value = 0.0;
          //is away goal?
          if (child.r_g < 0){
            sub_value = n.c_occs[k]*1.0;
          }
          //is home goal?
          else if(child.r_g > 0){
            sub_value = 0.0;
          }
          else{
            sub_value = n.c_occs[k]*child.curr_value[2];
          }
          if (qstar <= sub_value){
            qstar = sub_value; 
          }
          value += sub_value;
        }
        n.curr_value[2] = value/n.occ;
        n.qstar[2] = qstar/n.occ;
        nodes[s_ids[s]] = n;
        curr_values[2] += std::abs(n.curr_value[2]);
      }
    }
    //backup values?
    //TODO
    //check convergence
    for(int j = 0; j < 3; j++){
      if(converged[j]) continue;
      if(((curr_values[j] - last_values[j]) / curr_values[j]) < c){
        converged[j] = true;
        std::cout << "Converged: " << j << "\n";
      }
      last_values[j] = curr_values[j];
    }
    //check if all converged
    bool all_converged = true;
    for(int j = 0; j < 3; j++){
      if(converged[j] == false){
        all_converged = false;
        break;
      } 
    }
    std::cout << i << "\n";
    if(all_converged) break;
  }
  std::cout << "Nr of iterations: " << iterations << "\n";
  return convert_map_to_matrix(nodes, nr_of_states);
}
