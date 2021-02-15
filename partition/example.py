import numpy as np
import partition.analyzers as analyzers
from partition.models.models import model_xiang_2020_robot_arm, model_simple, model_dynamics, random_model
import argparse
import time
import os

if __name__ == '__main__':
    # Import all deps

    np.random.seed(seed=0)

    parser = argparse.ArgumentParser(description='Analyze a NN.')
    parser.add_argument('--model', default='robot_arm',
                        help='which NN to analyze (default: robot_arm)')
    parser.add_argument('--activation', default='tanh',
                        help='nonlinear activation fn in NN (default: tanh)')
    parser.add_argument('--partitioner', default='GreedySimGuided',
                        help='which partitioner to use (default: GreedySimGuided)')
    parser.add_argument('--propagator', default='CROWN_LIRPA',
                        help='which propagator to use (default: CROWN_LIRPA)')
    parser.add_argument('--term_type', default='time_budget',
                        help='type of condition to terminate (default: time_budget)')
    parser.add_argument('--term_val', default=2., type=float,
                        help='value of condition to terminate (default: 2)')
    parser.add_argument('--interior_condition', default='lower_bnds',
                        help='type of bound to optimize for (default: lower_bnds)')
    parser.add_argument('--num_simulations', default=1e4,
                        help='how many MC samples to begin with (default: 1e4)')
    
    parser.add_argument('--save_plot', dest='save_plot', action='store_true',
                        help='whether to save the visualization')
    parser.add_argument('--skip_save_plot', dest='feature', action='store_false')
    parser.set_defaults(save_plot=True)
    
    parser.add_argument('--show_plot', dest='show_plot', action='store_true',
                        help='whether to show the visualization')
    parser.add_argument('--skip_show_plot', dest='show_plot', action='store_false')
    parser.set_defaults(show_plot=False)
    
    parser.add_argument('--show_input', dest='show_input', action='store_true',
                        help='whether to show the input partition in the plot')
    parser.add_argument('--skip_show_input', dest='show_input', action='store_false')
    parser.set_defaults(show_input=True)
    
    parser.add_argument('--show_output', dest='show_output', action='store_true',
                        help='whether to show the output set in the plot')
    parser.add_argument('--skip_show_output', dest='show_output', action='store_false')
    parser.set_defaults(show_output=True)

    parser.add_argument('--input_plot_labels', metavar='N', default=["Input", None], type=str, nargs='+',
                        help='x and y labels on input partition plot (default: ["Input", None])')
    parser.add_argument('--output_plot_labels', metavar='N', default=["Output", None], type=str, nargs='+',
                        help='x and y labels on output partition plot (default: ["Output", None])')
    parser.add_argument('--input_plot_aspect', default="auto",
                        help='aspect ratio on input partition plot (default: auto)')
    parser.add_argument('--output_plot_aspect', default="auto",
                        help='aspect ratio on output partition plot (default: auto)')

    args = parser.parse_args()

    # Choose experiment settings
    ##############
    # LSTM
    ###############
    # ## A disastrous hack...
    # import sys, os, auto_LiRPA
    # sequence_path = os.path.dirname(os.path.dirname(auto_LiRPA.__file__))+'/examples/sequence'
    # sys.path.append(sequence_path)
    # from lstm import LSTM
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--seed", type=int, default=0)
    # parser.add_argument("--device", type=str, default="cpu", choices=["cuda", "cpu"])
    # parser.add_argument("--norm", type=int, default=2)
    # parser.add_argument("--eps", type=float, default=0.1)
    # parser.add_argument("--num_epochs", type=int, default=20)  
    # parser.add_argument("--batch_size", type=int, default=128)
    # parser.add_argument("--num_slices", type=int, default=8)
    # parser.add_argument("--hidden_size", type=int, default=64)
    # parser.add_argument("--num_classes", type=int, default=10) 
    # parser.add_argument("--input_size", type=int, default=784)
    # parser.add_argument("--lr", type=float, default=5e-3)
    # parser.add_argument("--dir", type=str, default=sequence_path+"/model", help="directory to load or save the model")
    # parser.add_argument("--num_epochs_warmup", type=int, default=1, help="number of epochs for the warmup stage when eps is linearly increased from 0 to the full value")
    # parser.add_argument("--log_interval", type=int, default=10, help="interval of printing the log during training")
    # args = parser.parse_args()   
    # torch_model = LSTM(args).to(args.device)
    # input_shape = (8,98)
    # input_range = np.zeros(input_shape+(2,))
    # input_range[-1,0:1,1] = 0.01
    # num_partitions = np.ones(input_shape, dtype=int)
    # partitioner = "SimGuided"
    # partitioner_hyperparams = {"tolerance_eps": 0.001}
    # # partitioner = "Uniform"
    # # num_partitions[-1,0] = 4
    # # partitioner_hyperparams = {"num_partitions": num_partitions}
    # propagator = "IBP (LIRPA)"
    # propagator_hyperparams = {}

    ##############
    # Simple FF network
    ###############
    if args.model == 'robot_arm':
        torch_model, model_info = model_xiang_2020_robot_arm(activation=args.activation)
        input_range = np.array([ # (num_inputs, 2)
                          [np.pi/3, 2*np.pi/3], # x0min, x0max
                          [np.pi/3, 2*np.pi/3], # x1min, x1max
        ])
    elif args.model == 'random_weights':
         neurons = [2,50,2]
         torch_model, model_info = random_model(activation=args.activation, neurons=neurons, seed=0)
         input_range = np.zeros((model_info['model_neurons'][0],2))
         input_range[:,1] = 1.
    else:
        raise NotImplementedError

    partitioner_hyperparams = {
        "num_simulations": args.num_simulations,
        "type": args.partitioner,
        "termination_condition_type": args.term_type, # other options: ["verify", "input_cell_size", "num_propagator_calls", "pct_improvement", "pct_error"]
        "termination_condition_value": args.term_val,
        "interior_condition": args.interior_condition,
        "make_animation": False,
        "show_animation": False,
    }
    propagator_hyperparams = {
        "type": args.propagator,
        "input_shape": input_range.shape[:-1],
    }

    # Run analysis & generate a plot
    analyzer = analyzers.Analyzer(torch_model)
    analyzer.partitioner = partitioner_hyperparams
    analyzer.propagator = propagator_hyperparams
    t_start = time.time()
    output_range, analyzer_info = analyzer.get_output_range(input_range)
    t_end = time.time()
    computation_time = t_end - t_start
    np.random.seed(seed=0)
   # output_range_exact = analyzer.get_exact_output_range(input_range)
    #if analyzer.partitioner["interior_condition"] == "convex_hull":
   #else:
    if  partitioner_hyperparams["interior_condition"] == "convex_hull":
        exact_hull = analyzer.get_exact_hull(input_range)

        error = analyzer.partitioner.get_error(exact_hull, analyzer_info["estimated_hull"])
    if  partitioner_hyperparams["interior_condition"] in ["lower_bnds", "linf"]:
        output_range_exact = analyzer.get_exact_output_range(input_range)

        error = analyzer.partitioner.get_error(output_range_exact, output_range)


   # output_range_exact = analyzer.get_exact_output_range(input_range)

   # error = analyzer.partitioner.get_error(output_range_exact, output_range)
    print("\n")
    print("{}+{}".format(partitioner_hyperparams["type"], propagator_hyperparams["type"]) )
   # print("Estimated output_range:\n", output_range)
    # print("True output_range:\n", output_range_exact)
    print("Number of propagator calls:", analyzer_info["num_propagator_calls"])
    print("Error: ", error)
    print("Number of partitions:", analyzer_info["num_partitions"])
    print("Computation time:",analyzer_info["computation_time"] )
    print("Number of iteration :",analyzer_info["num_iteration"] )
    print("Error (inloop) :",analyzer_info["estimation_error"] )
  #  print(output_range , analyzer_info["estimated_hull"] )

    if args.save_plot:
        save_dir = "{}/../results/analyzer/".format(os.path.dirname(os.path.abspath(__file__)))
        os.makedirs(save_dir, exist_ok=True)

        # Ugly logic to embed parameters in filename:
        pars = '_'.join([str(key)+"_"+str(value) for key, value in sorted(partitioner_hyperparams.items(), key=lambda kv: kv[0]) if key not in ["make_animation", "show_animation", "type"]])
        pars2 = '_'.join([str(key)+"_"+str(value) for key, value in sorted(propagator_hyperparams.items(), key=lambda kv: kv[0]) if key not in ["input_shape", "type"]])
        model_str = args.model + '_' + args.activation + '_'
        analyzer_info["save_name"] = save_dir+model_str+partitioner_hyperparams['type']+"_"+propagator_hyperparams['type']+"_"+pars
        if len(pars2) > 0:
            analyzer_info["save_name"] = analyzer_info["save_name"] + "_" + pars2
        analyzer_info["save_name"] = analyzer_info["save_name"] + ".png"
        
        # Plot shape/label settings
        labels = {"input": [l if l != 'None' else None for l in args.input_plot_labels], "output": [l if l is not 'None' else None for l in args.output_plot_labels]}
        aspects = {"input": args.input_plot_aspect, "output": args.output_plot_aspect}

        # Generate the plot & save
        analyzer.visualize(input_range, output_range, show=args.show_plot, show_samples=True, show_legend=False, 
            show_input=args.show_input, show_output=args.show_output, 
            title=None, labels=labels, aspects=aspects, **analyzer_info)
    
    print("done.")