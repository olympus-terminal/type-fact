#!/usr/bin/env python3
"""Terminal typing game — screening edition with signed results.

Exports a cryptographically signed JSON file containing per-round WPM,
accuracy, and raw keystroke timings.  Results can be verified offline with:

    python typing_game_screening.py --verify results_<name>_<ts>.json

Set TYPEFACT_SECRET in the environment to use a custom signing key.
"""

import argparse
import curses
import hashlib
import hmac
import json
import os
import random
import re
import sys
import time
import webbrowser

SENTENCES = [
    # ── Computer Science fundamentals (70) ──────────────────────────────────────
    "Dijkstra's algorithm finds the shortest path between nodes in a weighted graph using a priority queue.",
    "A hash table achieves average O(1) lookup by mapping keys to array indices through a hash function.",
    "The halting problem proved that no algorithm can determine whether an arbitrary program will finish running.",
    "Quicksort has O(n log n) average time complexity but degrades to O(n squared) with poor pivot choices.",
    "TCP guarantees reliable delivery by using sequence numbers, acknowledgments, and retransmission of lost packets.",
    "A B-tree keeps data sorted and allows searches, insertions, and deletions in logarithmic time for databases.",
    "The CAP theorem states a distributed system cannot simultaneously guarantee consistency, availability, and partition tolerance.",
    "Public key cryptography uses a pair of keys so that data encrypted with one can only be decrypted by the other.",
    "Garbage collection automatically reclaims memory by tracing which objects are still reachable from root references.",
    "A Turing machine is a mathematical model of computation that defines what it means for a function to be computable.",
    "MapReduce processes large datasets in parallel by splitting work across nodes then combining the partial results.",
    "The fast Fourier transform reduces the complexity of computing the discrete Fourier transform from O(n squared) to O(n log n).",
    "Conway's Game of Life shows that simple cellular automaton rules can produce complex emergent behavior.",
    "Huffman coding builds an optimal prefix-free binary code by repeatedly merging the two least frequent symbols.",
    "Version control systems like Git use directed acyclic graphs where each commit points to its parent commits.",
    "Cache locality matters because accessing nearby memory addresses is orders of magnitude faster than random access.",
    "The Byzantine Generals Problem asks how distributed nodes can reach consensus when some nodes may act maliciously.",
    "Bloom filters use multiple hash functions to test set membership with no false negatives but possible false positives.",
    "Regular expressions are equivalent in power to finite automata and cannot parse context-free languages like HTML.",
    "Unix pipes compose small programs by connecting stdout of one process to stdin of the next through a kernel buffer.",
    "A binary search halves the search space with each comparison, finding any element in a sorted array in O(log n) time.",
    "Merkle trees let you verify the integrity of large datasets by comparing only a single root hash value.",
    "The A* search algorithm combines actual path cost with a heuristic estimate to find optimal paths efficiently.",
    "A red-black tree guarantees O(log n) insertions and deletions by enforcing coloring rules that keep the tree balanced.",
    "DNS resolves human-readable domain names into IP addresses using a distributed hierarchical lookup system.",
    "Paxos achieves consensus among distributed nodes even when some participants fail or messages are lost in transit.",
    "A compiler converts high-level source code into machine instructions through lexing, parsing, and code generation phases.",
    "Virtual memory lets processes use more address space than physical RAM by swapping pages to and from disk.",
    "The dining philosophers problem illustrates how concurrent resource access can lead to deadlock without careful design.",
    "CRDTs allow multiple replicas to be updated independently and always converge to the same state without coordination.",
    "An LRU cache evicts the least recently accessed item first, exploiting temporal locality in access patterns.",
    "The RSA algorithm derives its security from the computational difficulty of factoring the product of two large primes.",
    "A skip list uses multiple layers of linked lists with random promotion to achieve O(log n) expected search time.",
    "Two's complement encoding lets hardware use the same addition circuit for both signed and unsigned integer arithmetic.",
    "The producer-consumer pattern uses a bounded buffer with semaphores to synchronize concurrent threads safely.",
    "ACID properties ensure database transactions are atomic, consistent, isolated, and durable even during system failures.",
    "Consistent hashing maps keys to servers in a ring so that adding or removing a node moves only a fraction of keys.",
    "The bellman equation in dynamic programming expresses an optimal solution as a combination of overlapping subproblems.",
    "TLS establishes an encrypted channel by using asymmetric keys to negotiate a shared symmetric session key.",
    "A trie stores strings character by character in a tree, enabling prefix-based search in time proportional to key length.",
    "Pipelining in CPUs overlaps the fetch, decode, and execute stages of successive instructions to increase throughput.",
    "Write-ahead logging ensures database crash recovery by recording changes to a log before applying them to disk.",
    "The stable marriage algorithm pairs two equally sized sets such that no pair would prefer each other over their match.",
    "An operating system's scheduler assigns CPU time slices to processes using policies like round-robin or priority queues.",
    "Reed-Solomon codes add redundant symbols to data so that the original message can be recovered from partial corruption.",
    "A semaphore is an integer-based synchronization primitive that controls access to shared resources among threads.",
    "Branch prediction allows a CPU to speculatively execute instructions before a conditional outcome is known.",
    "The AES block cipher encrypts data in 128-bit blocks through multiple rounds of substitution and permutation steps.",
    "A disjoint-set data structure with union by rank and path compression performs operations in nearly O(1) amortized time.",
    "Ethernet uses CSMA/CD to detect collisions on a shared medium and retransmit after a random backoff interval.",
    "Topological sorting arranges a directed acyclic graph into a linear order that respects all edge dependencies.",
    "Copy-on-write lets the fork system call create a child process without immediately duplicating the parent's memory pages.",
    "The Cooley-Tukey algorithm recursively splits a DFT into smaller transforms, but radix-4 variants reduce multiplies further.",
    "NAT allows multiple devices on a private network to share a single public IP address by rewriting packet headers.",
    "A suffix array stores all suffixes of a string in sorted order, enabling fast substring searches in O(m log n) time.",
    "Shannon entropy quantifies the minimum average number of bits needed to encode symbols from a given distribution.",
    "Lazy evaluation delays computation until the result is actually needed, enabling efficient work with infinite data streams.",
    "The Raft consensus protocol elects a leader that manages log replication across a cluster of distributed servers.",
    "Out-of-order execution lets a CPU rearrange instruction scheduling dynamically to avoid stalls from data dependencies.",
    "Page tables map virtual addresses to physical frames, letting each process believe it has its own contiguous memory space.",
    "Context switching saves and restores CPU register state so the operating system can multiplex processes on one core.",
    "Kruskal's algorithm builds a minimum spanning tree by adding the cheapest edge that does not create a cycle.",
    "Memory-mapped I/O lets programs read and write to hardware devices using the same instructions they use for RAM access.",
    "The SYN flood attack exploits the TCP three-way handshake by sending many connection requests without completing them.",
    "A B+ tree stores all data in leaf nodes linked together, making range queries and sequential access highly efficient.",
    "Register allocation assigns frequently used variables to CPU registers to avoid slower memory access during execution.",
    "Vector clocks track causal ordering of events in distributed systems by maintaining a counter per participating node.",
    "The NP-completeness of Boolean satisfiability means any NP problem can be reduced to checking a logical formula.",
    "An interrupt signals the CPU to pause its current work and handle an urgent event like a keystroke or disk completion.",
    "Erasure coding splits data into fragments with redundancy so the original can be rebuilt from any sufficient subset.",

    # ── Machine Learning (63) ───────────────────────────────────────────────────
    "Gradient descent updates model parameters by moving in the direction that most reduces the loss function.",
    "Batch normalization stabilizes training by normalizing layer inputs, allowing higher learning rates and faster convergence.",
    "The bias-variance tradeoff shows that reducing one source of error often increases the other in predictive models.",
    "Dropout randomly deactivates neurons during training, forcing the network to learn redundant representations that generalize better.",
    "Convolutional neural networks exploit spatial locality by sharing filter weights across all positions in the input.",
    "Cross-validation estimates model performance by repeatedly training on subsets of data and testing on the held-out fold.",
    "Support vector machines find the maximum-margin hyperplane that separates classes with the largest possible gap.",
    "Random forests reduce overfitting by averaging predictions from many decision trees trained on bootstrap samples.",
    "Principal component analysis finds orthogonal directions of maximum variance to reduce the dimensionality of data.",
    "The curse of dimensionality means that distance metrics become less meaningful as the number of features grows.",
    "Backpropagation computes gradients efficiently by applying the chain rule layer by layer from output back to input.",
    "Xavier initialization sets weights so that the variance of activations stays constant across layers at the start of training.",
    "Learning rate schedules like cosine annealing gradually reduce the step size to help optimization converge to flatter minima.",
    "Data augmentation artificially expands training sets by applying transformations like rotations, flips, and color jitter.",
    "Ensemble methods combine multiple models to reduce variance and improve predictions beyond any single model.",
    "L1 regularization induces sparsity by driving small weights exactly to zero during optimization.",
    "The vanishing gradient problem in deep networks occurs when repeated multiplication shrinks gradients toward zero.",
    "LSTM networks use forget, input, and output gates to control information flow through their cell state.",
    "The softmax function converts a vector of raw logits into a probability distribution that sums to one.",
    "K-means clustering minimizes the sum of squared distances between each point and its nearest centroid.",
    "Residual connections in ResNets allow gradients to flow directly through skip connections during training.",
    "The Adam optimizer combines momentum with per-parameter adaptive learning rates using moving averages.",
    "Precision measures the fraction of positive predictions that are correct, reducing false positive impact.",
    "Recall measures the fraction of actual positives that are correctly identified by the classifier.",
    "The ROC curve plots true positive rate against false positive rate across classification thresholds.",
    "Gated recurrent units simplify LSTMs by merging the cell state and hidden state into one vector.",
    "Weight decay adds a penalty proportional to the squared magnitude of weights to the loss function.",
    "The kernel trick lets SVMs operate in high-dimensional spaces without explicitly computing coordinates.",
    "Batch gradient descent computes the loss over all training examples before updating model parameters.",
    "Stochastic gradient descent updates weights after each individual example, adding beneficial noise.",
    "Feature scaling ensures that no single variable dominates the loss surface due to its numeric range.",
    "Early stopping halts training when validation loss begins to increase, acting as implicit regularization.",
    "The information bottleneck theory suggests deep networks compress input data while preserving label information.",
    "Depthwise separable convolutions factorize standard convolutions to drastically reduce parameter count.",
    "Label smoothing replaces hard target labels with soft targets to prevent overconfident predictions.",
    "The F1 score is the harmonic mean of precision and recall, balancing both metrics equally.",
    "Gradient clipping caps the norm of gradients during training to prevent exploding gradient updates.",
    "One-hot encoding represents categorical variables as binary vectors with exactly one active element.",
    "The EM algorithm alternates between estimating latent variables and maximizing the expected log-likelihood.",
    "Logistic regression models the log-odds of a binary outcome as a linear function of the features.",
    "The hinge loss used in SVMs penalizes predictions that fall within the margin boundary, not just errors.",
    "Mean squared error is sensitive to outliers because it squares the difference between predicted and true values.",
    "The Huber loss combines squared error for small residuals with absolute error for large ones.",
    "The reparameterization trick in VAEs enables backpropagation through stochastic sampling operations.",
    "Group normalization divides channels into groups and normalizes within each, removing batch dependence.",
    "Mixup training creates virtual examples by taking convex combinations of pairs of inputs and labels.",
    "The KL divergence measures how one probability distribution diverges from a second reference distribution.",
    "AdaGrad adapts learning rates per parameter by accumulating the sum of squared historical gradients.",
    "Elastic net regularization combines L1 and L2 penalties to balance sparsity with weight shrinkage.",
    "Max pooling reduces spatial dimensions by selecting the largest activation in each local receptive field.",
    "The naive Bayes classifier assumes all features are conditionally independent given the class label.",
    "Gradient boosting builds an ensemble by sequentially fitting weak learners to the residual errors.",
    "Spectral normalization constrains the Lipschitz constant of neural network layers for stable training.",
    "The contrastive loss pulls similar pairs closer and pushes dissimilar pairs apart in embedding space.",
    "Layer normalization computes statistics across all features for each example, independent of batch size.",
    "Decision trees split data by choosing the feature and threshold that maximize information gain at each node.",
    "The learning rate warmup strategy starts with a small rate and gradually increases it to the target value.",
    "Dilated convolutions expand the receptive field without increasing parameters by inserting gaps in the kernel.",
    "The triplet loss trains embeddings by requiring an anchor to be closer to a positive than to a negative.",
    "Target encoding replaces a categorical feature with the mean of the target variable for each category.",
    "RMSProp divides the learning rate by an exponentially decaying average of squared gradients per parameter.",
    "Sigmoid activation squashes its input to the range zero to one, making it useful for binary classification.",
    "Cyclical learning rates oscillate between bounds during training, helping escape sharp local minima.",

    # ── Artificial Intelligence (67) ────────────────────────────────────────────
    "The attention mechanism lets neural networks weigh the relevance of each input element when producing an output.",
    "Transformers replaced recurrence with self-attention, enabling parallel training on sequences and scaling to billions of parameters.",
    "Reinforcement learning trains agents by rewarding desired behavior, requiring no labeled examples of correct actions.",
    "AlphaGo combined Monte Carlo tree search with deep neural networks to defeat the world champion at the game of Go.",
    "Word embeddings like Word2Vec capture semantic relationships so that king minus man plus woman approximately equals queen.",
    "Generative adversarial networks train a generator and discriminator in competition, producing increasingly realistic synthetic data.",
    "The transformer architecture uses positional encodings because self-attention alone has no notion of token order.",
    "RLHF fine-tunes language models using human preference rankings to align model outputs with human values and intentions.",
    "Mixture of experts routes each input to a subset of specialized sub-networks, increasing capacity without proportional compute cost.",
    "Neural architecture search automates the design of network topologies by treating architecture choices as a search problem.",
    "Retrieval-augmented generation grounds language model responses in external documents to reduce hallucination.",
    "Knowledge distillation transfers learned behavior from a large teacher model to a smaller student model with minimal accuracy loss.",
    "Diffusion models generate images by learning to reverse a gradual noising process, one denoising step at a time.",
    "Chain-of-thought prompting improves reasoning in large language models by eliciting intermediate steps before the final answer.",
    "The lottery ticket hypothesis proposes that dense networks contain sparse subnetworks that can match full model performance.",
    "Beam search explores multiple candidate sequences in parallel to find higher-quality text generations.",
    "Byte-pair encoding iteratively merges the most frequent character pairs to build a subword vocabulary.",
    "The Viterbi algorithm finds the most likely hidden state sequence in a hidden Markov model efficiently.",
    "Contrastive learning trains encoders by pulling similar pairs closer and pushing dissimilar pairs apart.",
    "Variational autoencoders learn a continuous latent space by maximizing a lower bound on data likelihood.",
    "The BLEU score measures translation quality by comparing n-gram overlap between output and reference text.",
    "Feature pyramids in object detectors fuse multi-scale feature maps to recognize objects at different sizes.",
    "Non-maximum suppression removes redundant overlapping bounding boxes by keeping only the highest-scoring one.",
    "Anchor boxes provide predefined aspect ratios that help object detectors predict bounding box offsets.",
    "The CTC loss function aligns variable-length input sequences to output labels without explicit alignment data.",
    "Spectrograms convert raw audio waveforms into time-frequency representations suitable for neural networks.",
    "Policy gradient methods optimize reinforcement learning policies directly by estimating reward gradients.",
    "Actor-critic algorithms combine a policy network for action selection with a value network for evaluation.",
    "Curriculum learning trains models on progressively harder examples, often improving convergence speed.",
    "Nucleus sampling selects tokens from the smallest set whose cumulative probability exceeds a threshold p.",
    "Temperature scaling divides logits by a constant before softmax to sharpen or flatten output distributions.",
    "Masked language modeling trains bidirectional encoders by predicting randomly hidden tokens in a sentence.",
    "Causal language modeling trains decoders by predicting each next token given only the preceding context.",
    "Rotary position embeddings encode position by rotating query and key vectors in pairs of dimensions.",
    "Flash attention reduces memory usage from quadratic to linear by computing attention in tiled blocks.",
    "Quantization compresses neural network weights from 32-bit floats to 4 or 8 bits with minimal accuracy loss.",
    "LoRA adapts large pretrained models by training small low-rank matrices inserted into frozen weight layers.",
    "Classifier-free guidance blends conditional and unconditional predictions to steer generative model output.",
    "The U-Net architecture uses symmetric encoder-decoder paths with skip connections for precise segmentation.",
    "Vision transformers divide images into fixed-size patches and process them as token sequences with attention.",
    "Sparse attention patterns reduce computation by restricting each token to attend only to nearby positions.",
    "Minimax search with alpha-beta pruning eliminates branches that cannot influence the final game decision.",
    "Semantic segmentation assigns a class label to every pixel in an image using fully convolutional networks.",
    "Reward shaping adds intermediate reward signals to sparse environments to accelerate policy learning.",
    "Tokenizers split text into subword units so models can handle rare words using combinations of common pieces.",
    "Multi-head attention runs several attention functions in parallel, letting each head learn different patterns.",
    "Gradient accumulation simulates larger batch sizes by summing gradients across multiple forward passes.",
    "Inverse reinforcement learning infers an unknown reward function by observing an expert's demonstrations.",
    "Neural radiance fields represent 3D scenes as continuous volumetric functions queried by position and angle.",
    "Speculative decoding uses a small draft model to propose tokens that a larger model verifies in parallel.",
    "Cross-entropy loss measures how well predicted probability distributions match the true label distribution.",
    "Embedding layers project discrete tokens into dense vector spaces where similar meanings cluster together.",
    "Residual learning reformulates layers to learn additive corrections, making identity mappings the default.",
    "Activation functions like ReLU introduce nonlinearity so that stacked layers can approximate any function.",
    "Self-supervised learning extracts training signal from unlabeled data by predicting masked or corrupted inputs.",
    "Federated learning trains a shared model across many devices without centralizing private user data.",
    "Transfer learning reuses features from a model trained on one task to accelerate learning on a related task.",
    "Monte Carlo dropout approximates Bayesian uncertainty by running inference multiple times with dropout enabled.",
    "The perceptron convergence theorem guarantees a linear classifier will find a solution if the data is separable.",
    "Attention heads in later transformer layers tend to capture long-range dependencies and abstract relationships.",
    "Positional interpolation extends a trained context window by rescaling position indices to unseen lengths.",
    "Top-k sampling restricts token generation to the k highest-probability candidates at each decoding step.",
    "Contrastive predictive coding learns representations by predicting future latent states from past context.",
    "Model parallelism splits a single neural network across multiple devices when it exceeds one GPU's memory.",
    "Cosine similarity measures the angle between two vectors, ignoring magnitude to focus on directional alignment.",
    "The attention sink phenomenon shows that early tokens accumulate disproportionate attention in long contexts.",
    "Mixed-precision training uses 16-bit floats for speed while keeping a 32-bit master copy for numerical stability.",

    # ── Computer Science fundamentals, batch 2 (83) ────────────────────────────
    "A just-in-time compiler translates bytecode into native machine code at runtime to optimize hot execution paths.",
    "An abstract syntax tree represents source code structure as a tree of nodes stripped of syntactic sugar and punctuation.",
    "Journaling file systems write metadata changes to a log before committing them, enabling fast recovery after a crash.",
    "An inode stores a file's metadata and block pointers but not its name, which is held by the directory entry.",
    "ZFS uses a copy-on-write model where modified blocks are written to new locations, preserving consistent snapshots on disk.",
    "RAID 5 stripes data across disks with distributed parity so the array can survive any single disk failure.",
    "Flash translation layers remap logical addresses to physical pages because NAND flash cells must be erased before rewrite.",
    "SSD wear leveling distributes write operations evenly across flash cells to prevent any single block from wearing out first.",
    "Lock-free data structures use atomic compare-and-swap operations to allow concurrent progress without mutual exclusion.",
    "A future represents a value that may not yet be available, letting callers chain dependent computations without blocking.",
    "The actor model encapsulates state within independent actors that communicate exclusively through asynchronous message passing.",
    "Software transactional memory groups read-write operations into atomic transactions that roll back on conflict.",
    "Compare-and-swap atomically replaces a memory value only if it matches the expected old value, enabling lock-free algorithms.",
    "Work-stealing schedulers let idle threads take tasks from busy threads' queues to balance parallel workloads dynamically.",
    "Model checking exhaustively explores all reachable states of a finite system to verify that a property holds everywhere.",
    "Proof assistants like Coq verify mathematical theorems by type-checking programs that encode proofs as typed lambda terms.",
    "The Curry-Howard correspondence establishes a direct mapping between logical proofs and well-typed functional programs.",
    "SAT solvers use conflict-driven clause learning to prune the search space when checking Boolean satisfiability problems.",
    "Temporal logic extends propositional logic with operators for reasoning about how truth values change over time.",
    "Binary decision diagrams compress Boolean functions into canonical directed graphs for efficient equivalence checking.",
    "The Miller-Rabin primality test uses modular exponentiation with random witnesses to detect composite numbers rapidly.",
    "The extended Euclidean algorithm computes modular multiplicative inverses, which are essential for many cryptographic schemes.",
    "The Chinese remainder theorem speeds modular arithmetic by decomposing computations into independent smaller-modulus parts.",
    "UDP provides connectionless datagram delivery with minimal overhead, trading reliability for lower latency than TCP.",
    "The QUIC protocol multiplexes streams over encrypted UDP connections, eliminating head-of-line blocking at the transport layer.",
    "BGP routers exchange reachability information between autonomous systems using path-vector routing to build the global internet.",
    "IP multicast delivers packets to a group of receivers simultaneously, avoiding the overhead of sending individual copies.",
    "Congestion control algorithms like CUBIC adjust the sending rate using a cubic function of time since the last loss event.",
    "The Ford-Fulkerson method computes maximum flow in a network by repeatedly finding augmenting paths from source to sink.",
    "Tarjan's algorithm finds all strongly connected components of a directed graph in a single depth-first search traversal.",
    "The four-color theorem states that every planar graph can be colored with at most four colors so no adjacent nodes match.",
    "Graph coloring assigns labels to vertices so that no two adjacent vertices share the same color using minimal colors.",
    "Edmonds' blossom algorithm solves maximum matching in general graphs by shrinking odd-length cycles into single nodes.",
    "The min-cut max-flow theorem states that the maximum flow through a network equals the capacity of its minimum cut.",
    "Kosaraju's algorithm finds strongly connected components by performing two depth-first searches on a graph and its transpose.",
    "The push-relabel algorithm computes maximum flow by pushing excess flow toward the sink using local height-based operations.",
    "Kuratowski's theorem characterizes planar graphs as those containing no subdivision of the complete graphs K5 or K3,3.",
    "Christofides' algorithm guarantees a tour within 1.5 times the optimal length for the metric traveling salesman problem.",
    "Generational garbage collection exploits the weak generational hypothesis that most objects die young.",
    "Reference counting frees memory immediately when an object count drops to zero but cannot reclaim cyclic references.",
    "Mark-and-sweep garbage collection traces all reachable objects from root pointers then frees every unmarked object.",
    "The card table in generational GC tracks old-to-young pointers so minor collections avoid scanning the entire heap.",
    "Concurrent mark-sweep collectors reduce pause times by tracing live objects while application threads keep running.",
    "A copying collector compacts live objects into one half of memory, eliminating fragmentation after each collection cycle.",
    "RISC architectures use fixed-length instructions and load-store design to simplify pipelining and increase clock speed.",
    "CISC instructions can operate directly on memory, reducing instruction count at the cost of more complex decoding logic.",
    "SIMD instructions apply one operation to multiple data elements in parallel using wide vector registers.",
    "VLIW processors rely on the compiler to schedule independent operations into long instruction words at compile time.",
    "Speculative execution runs instructions past an unresolved branch and discards the results if the prediction was wrong.",
    "Register renaming eliminates false data dependencies by mapping architectural registers to a larger physical register file.",
    "Predicated execution converts branches into conditional instructions so the pipeline never stalls on a misprediction.",
    "Lambda calculus expresses all computation using only anonymous functions, variable binding, and function application.",
    "Monads in Haskell sequence side effects by chaining computations that each return a wrapped value with a bind operator.",
    "Continuations capture the rest of a computation as a first-class value, enabling custom control flow like coroutines.",
    "Dependent types allow the return type of a function to vary based on the value of its arguments, enabling proofs in code.",
    "Rust borrow checker enforces that each value has exactly one mutable reference or any number of immutable references.",
    "Hindley-Milner type inference determines the most general type of an expression without requiring any type annotations.",
    "Algebraic data types model values as tagged unions and products, making illegal states unrepresentable in the type system.",
    "A cyclic redundancy check detects accidental data corruption by treating the message as a polynomial divided by a generator.",
    "Hamming codes correct single-bit errors by placing parity bits at power-of-two positions within each data block.",
    "Turbo codes approach the Shannon limit by iteratively decoding two parallel convolutional codes linked by an interleaver.",
    "LDPC codes use sparse parity-check matrices and belief propagation decoding to achieve near-capacity error correction.",
    "A checksum detects errors by summing data words and comparing the result to a value appended during transmission.",
    "Convolutional codes encode data by passing input bits through a sliding shift register with modular-two adders.",
    "Multi-version concurrency control lets readers access a consistent snapshot without blocking concurrent writers.",
    "LSM trees buffer writes in memory and flush sorted runs to disk, merging them in the background for write-heavy workloads.",
    "Column stores compress and scan data efficiently for analytics by storing each attribute in a separate contiguous file.",
    "Query optimizers estimate plan costs using table statistics and cardinality estimates to choose join order and access paths.",
    "Write-ahead log variants like ARIES use physiological logging and fuzzy checkpoints for efficient crash recovery.",
    "A covering index includes all columns a query needs so the database can answer it without touching the base table.",
    "The Shannon-Hartley theorem sets an upper bound on channel capacity based on bandwidth and signal-to-noise ratio.",
    "Kolmogorov complexity measures a string information content as the length of the shortest program that produces it.",
    "Lossless compression cannot reduce every possible input because there are more strings than short descriptions.",
    "Lossy compression discards perceptually irrelevant details, achieving ratios that lossless methods cannot match.",
    "Arithmetic coding encodes an entire message as a single fraction, approaching the Shannon entropy limit more closely.",
    "Mutual information quantifies how much knowing one random variable reduces uncertainty about another.",
    "Zero-knowledge proofs let a prover convince a verifier that a statement is true without revealing any underlying data.",
    "Homomorphic encryption allows computation on ciphertext so that decrypting the result matches operating on plaintext.",
    "Side-channel attacks extract secret keys by measuring physical leakage such as timing, power consumption, or emanations.",
    "Diffie-Hellman key exchange lets two parties derive a shared secret over an insecure channel using modular exponentiation.",
    "Certificate authorities sign digital certificates to bind a public key to an identity for trusted communication.",
    "Elliptic curve cryptography achieves equivalent security to RSA with much shorter keys using points on algebraic curves.",
    "A message authentication code verifies both the integrity and authenticity of a message using a shared secret key.",

    # ── Machine Learning, batch 2 (50) ──────────────────────────────────────────
    "Bayesian inference updates a prior distribution with observed data to produce a posterior distribution over parameters.",
    "Gaussian processes define a distribution over functions and use a kernel to measure similarity between inputs.",
    "Markov chain Monte Carlo draws correlated samples from a posterior by constructing a Markov chain at equilibrium.",
    "Variational inference approximates an intractable posterior by optimizing a simpler distribution to minimize divergence.",
    "Bayesian optimization selects the next query point by maximizing an acquisition function over a surrogate model.",
    "The do-calculus provides rules for identifying causal effects from observational data using directed acyclic graphs.",
    "Instrumental variables estimate causal effects by exploiting a variable that affects treatment but not the outcome directly.",
    "Propensity score matching balances treated and control groups by pairing units with similar treatment probabilities.",
    "Counterfactual reasoning asks what outcome would have occurred had a different intervention been applied to a unit.",
    "The backdoor criterion identifies sufficient adjustment sets for estimating causal effects from observational data.",
    "Message passing neural networks update each node by aggregating learned messages from its immediate neighbors.",
    "Graph convolutional networks generalize spatial convolutions to irregular graph structures via spectral filtering.",
    "Node-level tasks in graph neural networks predict properties of individual vertices using local neighborhood features.",
    "Over-smoothing in deep graph networks causes node representations to converge, losing discriminative information.",
    "Graph-level readout functions aggregate all node embeddings into a single fixed-size vector for classification.",
    "SimCLR learns visual representations by maximizing agreement between differently augmented views of the same image.",
    "BYOL trains without negative pairs by using a momentum-updated target network to provide regression targets.",
    "DINO distills knowledge from a momentum teacher into a student network using self-supervised vision transformers.",
    "Masked autoencoders reconstruct randomly masked image patches to learn rich visual representations without labels.",
    "Barlow Twins reduces redundancy by driving the cross-correlation matrix of twin embeddings toward the identity.",
    "A convex loss function guarantees that any local minimum is also the global minimum of the optimization problem.",
    "Saddle points have zero gradient but mixed curvature, slowing optimization more than local minima in high dimensions.",
    "The Hessian matrix captures second-order curvature information and enables more precise parameter update steps.",
    "Natural gradient descent preconditions updates using the Fisher information matrix to respect parameter geometry.",
    "Polyak averaging computes a running mean of iterates to reduce variance and improve convergence of final parameters.",
    "Demographic parity requires that a classifier's positive prediction rate is equal across all protected groups.",
    "Equalized odds constrains a model to have equal true positive and false positive rates across demographic groups.",
    "Calibration curves plot predicted probabilities against observed frequencies to assess a model's confidence accuracy.",
    "Platt scaling fits a logistic regression on model logits to produce well-calibrated probability estimates post hoc.",
    "Disparate impact measures fairness by comparing the selection rate of a disadvantaged group to the advantaged group.",
    "Autoregressive models predict each time step as a function of a fixed number of preceding observations in a series.",
    "Exponential smoothing assigns exponentially decreasing weights to older observations for adaptive trend forecasting.",
    "State space models capture time series dynamics through latent states that evolve according to transition equations.",
    "Temporal convolutional networks apply causal dilated convolutions along the time axis for efficient sequence modeling.",
    "Fourier features map temporal inputs into sinusoidal basis functions to capture periodic patterns in time series data.",
    "XGBoost builds an ensemble of decision trees using second-order gradient statistics for efficient split selection.",
    "CatBoost handles categorical features natively using ordered target statistics to avoid prediction shift during training.",
    "Permutation feature importance measures how much predictive performance drops when a single feature is randomly shuffled.",
    "SHAP values assign each feature an additive contribution to a prediction based on cooperative game theory axioms.",
    "Partial dependence plots show the marginal effect of one or two features on a model's predicted outcome.",
    "Pool-based active learning selects the most informative examples from a large unlabeled pool for human annotation.",
    "Uncertainty sampling queries the instance for which the current model has the least confident prediction.",
    "Stream-based active learning decides whether to label each incoming instance as it arrives in a single pass.",
    "Query-by-committee selects examples where an ensemble of models disagrees most to maximize information gain.",
    "Expected model change selects the sample that would most alter current parameters if its label were known.",
    "Angular loss penalizes deviations from a target angle at the negative point in an anchor-positive-negative triangle.",
    "Proxy-based metric learning assigns learnable proxy vectors to classes, avoiding costly all-pairs mining in a batch.",
    "Hard negative mining focuses training on the closest incorrect matches to sharpen decision boundaries in embedding space.",
    "Multi-similarity loss jointly weighs self-similarity, positive similarity, and negative similarity within each mini-batch.",
    "Normalized softmax loss projects embeddings onto a hypersphere and optimizes angular margins between class clusters.",

    # ── Artificial Intelligence, batch 2 (76) ───────────────────────────────────
    "Rapidly exploring random trees build motion plans by incrementally sampling and connecting collision-free configurations.",
    "Simultaneous localization and mapping lets a robot build a map of an unknown environment while tracking its own pose.",
    "Inverse kinematics computes the joint angles a robotic arm needs to place its end effector at a desired position.",
    "Probabilistic roadmaps precompute a graph of collision-free samples so robots can quickly query feasible motion plans.",
    "Task and motion planning integrates symbolic action sequences with continuous trajectory optimization for robot manipulation.",
    "Emergent behavior in multi-agent systems arises when simple local interaction rules produce complex collective patterns.",
    "Swarm intelligence algorithms like ant colony optimization solve routing problems using stigmergic pheromone communication.",
    "Independent Q-learning in multi-agent settings suffers from environment non-stationarity caused by co-adapting agents.",
    "Communication protocols in multi-agent reinforcement learning let agents share observations to coordinate joint strategies.",
    "Competitive self-play trains agents by pairing them against copies of themselves to discover increasingly robust policies.",
    "Particle swarm optimization updates candidate solutions by blending each particle's personal best with the global best.",
    "WaveNet generates raw audio waveforms using dilated causal convolutions that capture long-range temporal dependencies.",
    "Mel spectrograms compress audio frequency bins onto the mel scale to approximate human perception of pitch differences.",
    "Speaker diarization segments an audio stream into homogeneous intervals and assigns each interval to a distinct speaker.",
    "Neural text-to-speech systems convert phoneme sequences into mel spectrograms that a vocoder renders as audible waveforms.",
    "Speaker verification compares voice embeddings extracted by a neural encoder to decide whether two utterances match.",
    "Optical flow estimates per-pixel motion vectors between consecutive video frames to capture apparent visual movement.",
    "Temporal modeling in video networks uses three-dimensional convolutions to learn joint spatial and temporal features.",
    "Video diffusion models generate temporally coherent frame sequences by denoising a three-dimensional latent tensor.",
    "Action recognition classifies human activities in video clips by pooling spatiotemporal features from backbone networks.",
    "Two-stream architectures process an RGB frame stream and an optical flow stream then fuse their predictions for video tasks.",
    "Temporal transformers model long-range dependencies across video frames by applying self-attention along the time axis.",
    "Tree-structured code generation predicts abstract syntax tree nodes top-down to guarantee syntactically valid programs.",
    "Program repair systems localize buggy statements and synthesize patches that pass an existing suite of test cases.",
    "Formal specification in program synthesis constrains the search space by requiring outputs to satisfy logical preconditions.",
    "Execution-guided synthesis prunes candidate programs early by running them on sample inputs and checking partial outputs.",
    "Neural program induction learns a latent execution trace from input-output examples without producing explicit source code.",
    "Linear probing trains a simple classifier on frozen model activations to test whether a layer encodes a specific feature.",
    "Circuit analysis traces how specific model components compose to implement an identifiable algorithmic behavior end to end.",
    "Sparse autoencoders decompose neural network activations into interpretable monosemantic feature directions in latent space.",
    "Feature visualization optimizes an input image to maximally activate a chosen neuron, revealing what pattern it detects.",
    "Activation patching isolates causal model components by replacing activations from one forward pass into another and measuring the effect.",
    "Logit lens projects intermediate transformer representations into vocabulary space to read off the model's evolving predictions.",
    "Reward hacking occurs when an agent exploits misspecified reward signals to achieve high return without intended behavior.",
    "Goodhart's law in machine learning warns that optimizing a proxy metric too aggressively degrades the true objective.",
    "Corrigibility requires that an agent does not resist or manipulate attempts by its operators to modify its objective.",
    "Mesa-optimization arises when a learned model internally implements its own optimization process with a potentially misaligned objective.",
    "Scalable oversight methods like debate and recursive reward modeling help supervisors evaluate outputs beyond their expertise.",
    "Neurosymbolic AI combines neural pattern recognition with symbolic reasoning to achieve structured generalization.",
    "Differentiable programming enables gradient-based optimization through arbitrary program structures including branches and loops.",
    "Neural theorem provers learn to select proof tactics by encoding logical formulas as continuous vector representations.",
    "Logic-neural integration embeds first-order logic constraints as differentiable loss terms to enforce rule consistency.",
    "Differentiable interpreters execute symbolic programs on neural embeddings so that discrete logic becomes end-to-end trainable.",
    "World models learn compressed latent dynamics from raw observations and use them to plan actions via imagination.",
    "Model-based reinforcement learning reduces sample complexity by training a policy inside a learned environment simulator.",
    "The Dreamer architecture learns a recurrent state-space model and optimizes long-horizon behavior entirely within latent rollouts.",
    "Learned simulators predict future states from current observations, allowing agents to rehearse actions without real interaction.",
    "Latent dynamics models encode transition functions in a compact hidden space to accelerate planning over long horizons.",
    "Sim-to-real transfer trains robot policies in simulation and deploys them on physical hardware with minimal fine-tuning.",
    "Domain randomization varies simulator parameters like friction and lighting so that trained policies generalize to the real world.",
    "Tactile sensing arrays on robotic grippers provide contact force feedback that enables dexterous in-hand object manipulation.",
    "Locomotion learning through deep reinforcement learning allows legged robots to traverse rough terrain without hand-tuned gaits.",
    "Embodied AI systems ground language understanding in physical interaction by linking words to sensorimotor experience.",
    "Contrastive pretraining aligns image and text embeddings in a shared space by maximizing agreement of matched pairs.",
    "Vision-language models generate image captions by attending over visual feature maps conditioned on a textual decoder state.",
    "Cross-modal attention layers let a transformer fuse information from different modalities such as images and text tokens.",
    "Image captioning models use an encoder-decoder architecture that converts visual features into natural language descriptions.",
    "Multimodal embedding spaces enable zero-shot image classification by comparing image vectors to text label embeddings.",
    "Conditional random fields model label dependencies in sequence tagging by defining potentials over neighboring output variables.",
    "Structured prediction methods output complex objects like parse trees or label sequences rather than single scalar values.",
    "Energy-based models assign a scalar energy to each input-output pair and predict the output that minimizes total energy.",
    "Structured output spaces require specialized loss functions that decompose over substructures to remain computationally tractable.",
    "Function calling lets language models invoke external APIs by emitting structured tool requests during text generation.",
    "Planning with large language models decomposes complex goals into ordered subtasks that can be executed and verified stepwise.",
    "Code execution as reasoning lets agents write and run programs to perform precise arithmetic or data transformations.",
    "Agentic tool use chains multiple function calls in a loop, where each observation informs the next action selection.",
    "Chinchilla scaling shows that compute-optimal training requires scaling model parameters and data tokens at roughly equal rates.",
    "Power law relationships link model loss to parameter count, dataset size, and compute budget with predictable exponents.",
    "Emergent abilities appear abruptly at certain model scales, with near-random performance below a critical parameter threshold.",
    "Compute-optimal training allocates a fixed compute budget by balancing model size against the number of training tokens processed.",
    "Scaling laws enable researchers to predict large model performance from smaller runs, reducing wasteful experimental searches.",
    "The KV cache stores previously computed key and value tensors so that autoregressive decoding avoids redundant computation.",
    "Paged attention manages the KV cache in non-contiguous memory blocks, reducing fragmentation and increasing serving throughput.",
    "Tensor parallelism splits individual weight matrices across multiple GPUs so that each device computes a shard of every layer.",
    "Continuous batching inserts new requests into a running batch as soon as earlier sequences finish, maximizing GPU utilization.",
    "Prefix caching reuses the KV cache of shared prompt prefixes across requests to eliminate repeated prefill computation.",

    # ── Cross-domain: hardware, systems, numerical, bioinformtic (25) ───────────
    "GPU tensor cores accelerate matrix multiplications by performing fused multiply-add operations on small matrix tiles in a single clock cycle.",
    "TPUs use systolic arrays that pass partial sums between processing elements to maximize data reuse and minimize memory access.",
    "Memory bandwidth often bottlenecks large model training more than raw compute because weight matrices exceed on-chip cache capacity.",
    "Data parallelism replicates the model across devices and partitions each minibatch so that each device computes gradients on a subset of examples.",
    "Ring-allreduce distributes gradient aggregation across workers in a ring topology so that communication cost is independent of worker count.",
    "Pipeline parallelism splits a model into sequential stages across devices and overlaps forward and backward passes using microbatching.",
    "The XLA compiler fuses sequences of elementwise operations into a single GPU kernel to eliminate intermediate memory reads and writes.",
    "Operator scheduling in ML compilers reorders graph nodes to overlap computation with data transfers across the PCIe or NVLink bus.",
    "Graph-level optimization passes such as constant folding and common subexpression elimination reduce redundant computation in neural network graphs.",
    "IEEE 754 floating point represents numbers using a sign bit, an exponent field, and a mantissa field to cover a wide dynamic range.",
    "Loss scaling in mixed-precision training multiplies the loss by a large constant to shift small gradient values into the representable float16 range.",
    "Kahan summation compensates for floating-point rounding errors by maintaining a running correction term that captures lost low-order bits.",
    "Numerical instability in softmax is avoided by subtracting the maximum logit from all logits before exponentiation to prevent overflow.",
    "Graphical models factorize joint distributions into local factors defined by edges in a directed or undirected graph.",
    "Belief propagation computes approximate marginal distributions by iteratively passing messages between neighboring nodes in a factor graph.",
    "Markov random fields encode conditional independence through an undirected graph where each node is independent of non-neighbors given its neighbors.",
    "The Needleman-Wunsch algorithm finds a global alignment of two biological sequences using dynamic programming with a scoring matrix and gap penalties.",
    "Smith-Waterman local alignment identifies the highest-scoring subsequence match between two sequences by allowing free end gaps in the scoring.",
    "Coevolutionary analysis of multiple sequence alignments reveals residue contacts that constrain three-dimensional protein structure prediction.",
    "HPC applications commonly use MPI collective operations like broadcast and scatter to coordinate data distribution across thousands of compute nodes.",
    "Human-in-the-loop systems route low-confidence predictions to annotators and retrain on the corrected labels.",
    "The bfloat16 format keeps the same eight-bit exponent as float32 but truncates the mantissa to seven bits, preserving dynamic range for deep learning.",
    "Gradient checkpointing trades compute for memory by recomputing intermediate activations during the backward pass rather than storing them all.",
    "BLAST uses short seed matches to quickly filter candidate regions before applying full dynamic programming alignment.",
    "Distributed training uses all-reduce collectives to synchronize gradients so every worker keeps identical model weights.",

    # ── AI for Biology (70) ─────────────────────────────────────────────────────
    "AlphaFold2 predicts protein 3D structures from amino acid sequences using an attention-based architecture called Evoformer.",
    "AlphaFold2 incorporates multiple sequence alignments and structural templates to iteratively refine atomic coordinate predictions.",
    "Protein structure prediction models output per-residue confidence scores called pLDDT to flag unreliable regions.",
    "RoseTTAFold uses a three-track neural network that simultaneously processes sequence, distance, and coordinate information.",
    "Energy landscape models represent protein folding as navigation toward a free energy minimum in conformational space.",
    "Inverse folding algorithms like ProteinMPNN design amino acid sequences that fold into a specified three-dimensional backbone.",
    "AlphaFold3 extends structure prediction to complexes of proteins with DNA, RNA, and small molecule ligands.",
    "Predicted aligned error matrices from AlphaFold2 reveal confidence in the relative positioning of protein domains.",
    "Enformer predicts gene expression from DNA sequence by modeling regulatory interactions up to 100 kilobases away.",
    "DeepVariant uses convolutional neural networks to call genetic variants from pileup images of aligned sequencing reads.",
    "DNA language models like the Nucleotide Transformer learn contextual representations of genomic sequences in a self-supervised manner.",
    "Basenji models predict cell-type-specific chromatin accessibility and histone modifications directly from DNA sequence.",
    "Splicing prediction models like SpliceAI identify cryptic splice variants that disrupt normal mRNA processing patterns.",
    "Epigenomic imputation methods use neural networks to predict missing histone marks from a subset of observed assays.",
    "Regulatory element classifiers trained on ATAC-seq data can distinguish active enhancers from promoters and silencers.",
    "Single-cell RNA sequencing analysis uses graph-based clustering on nearest neighbor graphs to identify distinct cell types.",
    "Variational autoencoders like scVI model the zero-inflated count distributions typical of single-cell gene expression data.",
    "RNA velocity infers future cell states by modeling the ratio of unspliced to spliced mRNA transcripts in each cell.",
    "Trajectory inference algorithms like Monocle3 reconstruct pseudotime orderings of cells along developmental lineages.",
    "Spatial transcriptomics methods combine gene expression profiles with tissue coordinates to map cell types in situ.",
    "Cell type annotation transfer methods project labels from reference atlases onto query single-cell datasets using embeddings.",
    "The scGPT foundation model learns cell representations from over 33 million single-cell transcriptomic profiles.",
    "Batch correction algorithms like Harmony integrate single-cell datasets from different experiments into a shared embedding.",
    "Graph neural networks on spatial transcriptomics data model cell-cell communication by encoding tissue neighborhood structure.",
    "ESM-2 learns protein representations by predicting masked amino acids in sequences drawn from millions of protein families.",
    "Protein language models capture structural contacts in their attention maps without any explicit structural supervision.",
    "Zero-shot mutation effect prediction scores variants by comparing wild-type and mutant log-likelihoods under a protein language model.",
    "ESM-1v predicts the functional effects of single amino acid substitutions using masked marginal probability scoring.",
    "Evolutionary scale modeling trains transformer architectures on databases containing over 250 million protein sequences.",
    "ESMFold predicts protein structures directly from single sequences without requiring multiple sequence alignment inputs.",
    "Protein language model embeddings cluster proteins by function and fold even without access to explicit homology labels.",
    "Fine-tuning protein language models on labeled fitness assays improves variant effect prediction for specific protein families.",
    "The ESM-IF1 inverse folding model generates sequences conditioned on backbone coordinates using a geometric transformer encoder.",
    "Protein language models assign higher likelihoods to residues at conserved functional sites than at rapidly evolving positions.",
    "Combining protein language model embeddings with structure-based features improves prediction of enzyme catalytic activity.",
    "Virtual screening uses docking scores to rank millions of candidate molecules against a protein target in silico.",
    "Molecular docking predicts the preferred orientation of a small molecule when it binds to a protein pocket.",
    "De novo molecule generation uses reinforcement learning to propose novel compounds optimized for desired properties.",
    "QSAR models map molecular descriptors to biological activity, enabling rapid potency estimation without wet-lab assays.",
    "ADMET prediction models estimate absorption, distribution, metabolism, excretion, and toxicity from molecular structure.",
    "Lead optimization applies multi-objective Bayesian methods to improve potency while maintaining favorable drug-like properties.",
    "Generative adversarial networks can produce novel molecular structures that satisfy multiple pharmacological constraints.",
    "Radiology AI detects lung nodules on chest CT scans with sensitivity comparable to experienced radiologists.",
    "Digital pathology models classify tumor subtypes from whole-slide images stained with hematoxylin and eosin.",
    "Retinal fundus imaging with deep learning can detect diabetic retinopathy and predict cardiovascular risk factors.",
    "U-Net architectures segment tumors and organs in medical images using skip connections for spatial precision.",
    "Anomaly detection in brain MRI uses autoencoders trained on healthy scans to flag unseen pathological regions.",
    "Attention-gated networks highlight diagnostically relevant regions in radiological scans without explicit bounding boxes.",
    "Recurrent neural networks applied to electronic health records can predict patient deterioration hours in advance.",
    "Bayesian optimization accelerates clinical trial design by adaptively allocating patients to the most promising arms.",
    "Cox proportional hazards models extended with neural networks capture nonlinear effects in survival analysis tasks.",
    "Biomarker discovery pipelines use gradient-based feature attribution to identify predictive lab values from patient data.",
    "Federated learning trains models across hospital networks without sharing raw patient records, preserving data privacy.",
    "Transformer models applied to longitudinal EHR sequences learn temporal patterns across diagnoses and medications.",
    "Causal inference methods help clinical AI distinguish treatment effects from confounding factors in observational data.",
    "SMILES encodes molecular graphs as character strings, enabling sequence models to generate and classify compounds.",
    "Graph neural networks operate directly on molecular graphs, treating atoms as nodes and bonds as edges.",
    "Three-dimensional conformer generation predicts the spatial arrangement of atoms that minimizes a molecule's free energy.",
    "Molecular fingerprints convert chemical structures into fixed-length bit vectors for rapid similarity searching.",
    "Equivariant neural networks respect rotational and translational symmetry when predicting molecular properties from 3D coordinates.",
    "Extended-connectivity fingerprints encode circular substructures around each atom to capture local chemical environments.",
    "Message-passing neural networks iteratively update atom features by aggregating information from neighboring atoms and bonds.",
    "Binding affinity prediction models estimate the strength of protein-ligand complexes from structural or sequence features.",
    "Machine learning potentials accelerate molecular dynamics simulations by replacing expensive quantum calculations with neural networks.",
    "Free energy perturbation enhanced by ML surrogate models reduces the computational cost of relative binding calculations.",
    "Scoring functions trained on co-crystal structures distinguish true binding poses from decoy docking conformations.",
    "Graph transformers model protein-ligand interactions by jointly encoding residue and atom-level contact information.",
    "Neural network potentials trained on density functional theory data reproduce quantum-level accuracy at a fraction of the cost.",
    "Interaction fingerprints encode hydrogen bonds, salt bridges, and hydrophobic contacts between a ligand and its binding site.",
    "Contrastive learning on protein-ligand pairs improves virtual screening by aligning representations of binding partners.",

    # ── Bash & Shell Tricks (70) ──────────────────────────────────────────────
    "Typing !! in bash repeats the entire last command, so sudo !! reruns the previous command with root privileges.",
    "The !$ shorthand expands to the last argument of the previous command, letting you reuse paths without retyping them.",
    "Quick substitution with ^old^new reruns the last command after replacing the first occurrence of old with new.",
    "Pressing Ctrl-R in bash starts reverse incremental search, letting you fuzzy-find commands from your shell history.",
    "The fc command opens your last command in your default editor, letting you fix and rerun complex one-liners easily.",
    "History expansion !:2 grabs the third argument of the last command, and !:1-3 selects a range of previous arguments.",
    "Using ${var:-default} expands to default when var is unset or empty, providing inline fallback values without an if statement.",
    "The expansion ${var%.*} strips the shortest matching suffix, removing a file extension from a filename stored in var.",
    "Using ${var##*/} strips the longest matching prefix through the last slash, extracting a basename without calling basename.",
    "The ${var//old/new} syntax performs global search-and-replace inside a variable without spawning a sed subprocess.",
    "The expansion ${#var} returns the character length of a variable, avoiding the need to pipe into wc -c for counting.",
    "Indirect variable references with ${!var} expand the value of var as a variable name, enabling dynamic variable lookup.",
    "Process substitution with <() presents command output as a temporary file descriptor, letting diff compare two command outputs directly.",
    "You can redirect stderr to stdout with 2>&1, or in bash 4+ use &> to redirect both stdout and stderr to the same destination.",
    "Bash can open TCP connections using /dev/tcp/host/port without netcat, enabling simple network checks in pure shell scripts.",
    "Here strings with <<< pass a single string as stdin to a command, avoiding the overhead of echo piped through a subshell.",
    "Heredocs with <<-EOF allow tab-indented content, stripping leading tabs so the document body can match your script indentation.",
    "Brace expansion {1..100} generates a sequence of numbers inline without calling seq, and {01..100} zero-pads automatically.",
    "Nested brace expansion like {a,b}{1,2} produces the Cartesian product a1 a2 b1 b2, useful for generating file name combinations.",
    "The globstar option in bash 4+ makes **/ match directories recursively, so ls **/*.py finds Python files at any depth.",
    "Extended globs enabled with shopt -s extglob let you write ?(pattern) for optional matches and !(pattern) for negation.",
    "Pressing Ctrl-Z suspends the foreground process, and typing bg then resumes it in the background without losing its state.",
    "The disown command detaches a background job from the shell session, preventing it from receiving SIGHUP when the terminal closes.",
    "Using coproc spawns a background process with bidirectional pipes, letting your script both write to and read from it.",
    "The trap command can catch signals like EXIT or ERR to run cleanup code, ensuring temporary files are removed on script failure.",
    "The wait command blocks until all background jobs finish and returns their exit statuses, enabling simple parallel task orchestration.",
    "Using type -a instead of which shows all locations of a command including aliases, builtins, and functions in search order.",
    "The command -v builtin is the POSIX-portable way to check if a command exists, preferred over which in shell scripts.",
    "The read -r -d '' var idiom reads an entire file or stream into a variable, preserving newlines without mangling backslashes.",
    "The mapfile builtin reads lines from stdin into an array variable, replacing fragile while-read loops for line-by-line processing.",
    "Using printf '%q' escapes a string for safe shell reuse, which is invaluable when programmatically building commands with special characters.",
    "The compgen -W builtin generates completion matches against a word list, useful for building custom tab-completion in scripts.",
    "Piping through tee writes output to both a file and stdout simultaneously, letting you log a pipeline stage without breaking the chain.",
    "Named pipes created with mkfifo act as persistent FIFO buffers between processes, enabling interprocess communication without temp files.",
    "Grouping commands with curly braces { cmd1; cmd2; } runs them in the current shell, unlike parentheses which spawn a subshell.",
    "Running set -euo pipefail at the top of a script makes it exit on errors, unset variables, and broken pipes.",
    "The shopt -s globstar option lets ** match files recursively through subdirectories in bash 4 and later.",
    "Setting shopt -s nullglob makes unmatched globs expand to nothing instead of being passed as literal strings.",
    "The set -x flag prints each command with its expanded arguments to stderr before execution for easy debugging.",
    "Enabling shopt -s extglob unlocks patterns like !(*.log) to match all files except those ending in .log.",
    "Declare -A in bash creates an associative array that lets you use arbitrary strings as keys instead of integers.",
    "The syntax ${arr[@]:2:3} slices a bash array, returning three elements starting at index two.",
    "Using ${!arr[@]} expands to all the keys of a bash array, which is essential for iterating associative arrays.",
    "The expression ${#arr[@]} returns the number of elements in a bash array, not the length of the first element.",
    "Appending to a bash array with arr+=(value) avoids the need to track the next available numeric index manually.",
    "Double brackets [[ ]] support regex matching with =~ and do not require quoting variables to prevent word splitting.",
    "The (( )) construct in bash evaluates arithmetic expressions and returns true when the result is nonzero.",
    "Inside [[ ]], the == operator performs glob-style pattern matching unless the right side is quoted as a literal.",
    "Bash supports a ternary-style expression with $(( condition ? value_if_true : value_if_false )) for inline arithmetic.",
    "The single bracket [ is a regular command called test, so it requires spaces around operators and careful quoting.",
    "The trap command with EXIT runs a cleanup function automatically when a script finishes, even if it exits early.",
    "Using trap '' SIGINT makes a script ignore interrupt signals, preventing users from stopping it with Ctrl-C.",
    "A common pattern creates temp files with mktemp and registers trap 'rm -f $tmpfile' EXIT to ensure cleanup.",
    "Trapping SIGUSR1 in a long-running script lets external processes trigger a config reload without restarting it.",
    "Multiple trap commands for the same signal overwrite each other, so combine all cleanup steps into one function.",
    "The exec 3>file command opens file descriptor 3 for writing, keeping it available for the rest of the script.",
    "Redirecting with >&3 sends output to a previously opened file descriptor, separating it from stdout and stderr.",
    "Closing a file descriptor with exec 3>&- frees it so the underlying file handle is released by the process.",
    "Reading from /dev/fd/N accesses file descriptor N as if it were a regular file, which works on Linux and macOS.",
    "Swapping stdout and stderr uses three steps: exec 3>&1 1>&2 2>&3 3>&- to route each to the other's destination.",
    "The ssh -J flag specifies a jump host, letting you reach a private server by bouncing through an intermediary.",
    "SSH ControlMaster multiplexing reuses a single TCP connection for multiple sessions, eliminating repeated handshakes.",
    "Running ssh user@host 'tar czf - /path' | tar xzf - copies a remote directory locally without needing scp or rsync.",
    "Local port forwarding with ssh -L 8080:dbhost:5432 tunnels a remote database port to your localhost securely.",
    "The sshfs command mounts a remote filesystem over SSH so you can edit remote files with local tools transparently.",
    "The /usr/bin/time -v command reports peak memory, page faults, and context switches that the bash builtin time omits.",
    "Setting TIMEFORMAT='%3R seconds' changes how the bash time keyword formats its output to show only real elapsed time.",
    "Adding PS4='+$(date +%s.%N) ' before set -x prefixes each trace line with a high-resolution timestamp for profiling.",
    "GNU parallel splits input across CPU cores and runs commands concurrently, unlike xargs which defaults to sequential.",
    "Using wait -n in bash 4.3 and later returns as soon as any background job finishes instead of waiting for all of them.",
]

WIKI_OVERRIDES = {
    "TCP guarantees reliable delivery by using sequence numbers, ": "Transmission_Control_Protocol",
    "Public key cryptography uses a pair of keys so that data enc": "Public-key_cryptography",
    "Garbage collection automatically reclaims memory by tracing ": "Garbage_collection_(computer_science)",
    "The fast Fourier transform reduces the complexity of computi": "Fast_Fourier_transform",
    "Conway's Game of Life shows that simple cellular automaton r": "Conway%27s_Game_of_Life",
    "Version control systems like Git use directed acyclic graphs": "Version_control",
    "Cache locality matters because accessing nearby memory addre": "Locality_of_reference",
    "The Byzantine Generals Problem asks how distributed nodes ca": "Byzantine_fault",
    "Bloom filters use multiple hash functions to test set member": "Bloom_filter",
    "Unix pipes compose small programs by connecting stdout of on": "Pipeline_(Unix)",
    "A binary search halves the search space with each comparison": "Binary_search",
    "DNS resolves human-readable domain names into IP addresses u": "Domain_Name_System",
    "Paxos achieves consensus among distributed nodes even when s": "Paxos_(computer_science)",
    "The dining philosophers problem illustrates how concurrent r": "Dining_philosophers_problem",
    "CRDTs allow multiple replicas to be updated independently an": "Conflict-free_replicated_data_type",
    "An LRU cache evicts the least recently accessed item first, ": "Cache_replacement_policies",
    "The RSA algorithm derives its security from the computationa": "RSA_(cryptosystem)",
    "Two's complement encoding lets hardware use the same additio": "Two%27s_complement",
    "The producer-consumer pattern uses a bounded buffer with sem": "Producer%E2%80%93consumer_problem",
    "ACID properties ensure database transactions are atomic, con": "ACID",
    "The bellman equation in dynamic programming expresses an opt": "Bellman_equation",
    "TLS establishes an encrypted channel by using asymmetric key": "Transport_Layer_Security",
    "Pipelining in CPUs overlaps the fetch, decode, and execute s": "Instruction_pipelining",
    "The stable marriage algorithm pairs two equally sized sets s": "Stable_marriage_problem",
    "An operating system's scheduler assigns CPU time slices to p": "Scheduling_(computing)",
    "Reed-Solomon codes add redundant symbols to data so that the": "Reed%E2%80%93Solomon_error_correction",
    "A semaphore is an integer-based synchronization primitive th": "Semaphore_(programming)",
    "Branch prediction allows a CPU to speculatively execute inst": "Branch_predictor",
    "The AES block cipher encrypts data in 128-bit blocks through": "Advanced_Encryption_Standard",
    "Ethernet uses CSMA/CD to detect collisions on a shared mediu": "Carrier-sense_multiple_access_with_collision_detection",
    "Topological sorting arranges a directed acyclic graph into a": "Topological_sorting",
    "The Cooley-Tukey algorithm recursively splits a DFT into sma": "Cooley%E2%80%93Tukey_FFT_algorithm",
    "NAT allows multiple devices on a private network to share a ": "Network_address_translation",
    "Shannon entropy quantifies the minimum average number of bit": "Entropy_(information_theory)",
    "Lazy evaluation delays computation until the result is actua": "Lazy_evaluation",
    "The Raft consensus protocol elects a leader that manages log": "Raft_(algorithm)",
    "Page tables map virtual addresses to physical frames, lettin": "Page_table",
    "Context switching saves and restores CPU register state so t": "Context_switch",
    "The SYN flood attack exploits the TCP three-way handshake by": "SYN_flood",
    "Vector clocks track causal ordering of events in distributed": "Vector_clock",
    "The NP-completeness of Boolean satisfiability means any NP p": "Boolean_satisfiability_problem",
    "An interrupt signals the CPU to pause its current work and h": "Interrupt",
    "Erasure coding splits data into fragments with redundancy so": "Erasure_code",
    "The bias-variance tradeoff shows that reducing one source of": "Bias%E2%80%93variance_tradeoff",
    "Convolutional neural networks exploit spatial locality by sh": "Convolutional_neural_network",
    "Cross-validation estimates model performance by repeatedly t": "Cross-validation_(statistics)",
    "Support vector machines find the maximum-margin hyperplane t": "Support-vector_machine",
    "Random forests reduce overfitting by averaging predictions f": "Random_forest",
    "The curse of dimensionality means that distance metrics beco": "Curse_of_dimensionality",
    "Learning rate schedules like cosine annealing gradually redu": "Learning_rate",
    "Ensemble methods combine multiple models to reduce variance ": "Ensemble_learning",
    "L1 regularization induces sparsity by driving small weights ": "Lasso_(statistics)",
    "LSTM networks use forget, input, and output gates to control": "Long_short-term_memory",
    "K-means clustering minimizes the sum of squared distances be": "K-means_clustering",
    "Residual connections in ResNets allow gradients to flow dire": "Residual_neural_network",
    "Precision measures the fraction of positive predictions that": "Precision_and_recall",
    "Recall measures the fraction of actual positives that are co": "Precision_and_recall",
    "The ROC curve plots true positive rate against false positiv": "Receiver_operating_characteristic",
    "Gated recurrent units simplify LSTMs by merging the cell sta": "Gated_recurrent_unit",
    "The kernel trick lets SVMs operate in high-dimensional space": "Kernel_method",
    "Batch gradient descent computes the loss over all training e": "Gradient_descent",
    "Early stopping halts training when validation loss begins to": "Early_stopping",
    "The information bottleneck theory suggests deep networks com": "Information_bottleneck_method",
    "Depthwise separable convolutions factorize standard convolut": "Depthwise_separable_convolution",
    "The F1 score is the harmonic mean of precision and recall, b": "F-score",
    "The EM algorithm alternates between estimating latent variab": "Expectation%E2%80%93maximization_algorithm",
    "The KL divergence measures how one probability distribution ": "Kullback%E2%80%93Leibler_divergence",
    "AdaGrad adapts learning rates per parameter by accumulating ": "Stochastic_gradient_descent#AdaGrad",
    "The naive Bayes classifier assumes all features are conditio": "Naive_Bayes_classifier",
    "RMSProp divides the learning rate by an exponentially decayi": "Stochastic_gradient_descent#RMSProp",
    "Sigmoid activation squashes its input to the range zero to o": "Sigmoid_function",
    "Cyclical learning rates oscillate between bounds during trai": "Learning_rate_schedule",
    "The attention mechanism lets neural networks weigh the relev": "Attention_(machine_learning)",
    "Transformers replaced recurrence with self-attention, enabli": "Transformer_(deep_learning_architecture)",
    "Word embeddings like Word2Vec capture semantic relationships": "Word_embedding",
    "Generative adversarial networks train a generator and discri": "Generative_adversarial_network",
    "The transformer architecture uses positional encodings becau": "Transformer_(deep_learning_architecture)",
    "RLHF fine-tunes language models using human preference ranki": "Reinforcement_learning_from_human_feedback",
    "Mixture of experts routes each input to a subset of speciali": "Mixture_of_experts",
    "Neural architecture search automates the design of network t": "Neural_architecture_search",
    "Retrieval-augmented generation grounds language model respon": "Retrieval-augmented_generation",
    "Knowledge distillation transfers learned behavior from a lar": "Knowledge_distillation",
    "Diffusion models generate images by learning to reverse a gr": "Diffusion_model",
    "Chain-of-thought prompting improves reasoning in large langu": "Chain-of-thought_prompting",
    "Byte-pair encoding iteratively merges the most frequent char": "Byte_pair_encoding",
    "The BLEU score measures translation quality by comparing n-g": "BLEU",
    "Feature pyramids in object detectors fuse multi-scale featur": "Feature_pyramid_network",
    "The CTC loss function aligns variable-length input sequences": "Connectionist_temporal_classification",
    "LoRA adapts large pretrained models by training small low-ra": "Low-rank_adaptation",
    "Classifier-free guidance blends conditional and unconditiona": "Classifier-free_diffusion_guidance",
    "Vision transformers divide images into fixed-size patches an": "Vision_transformer",
    "Minimax search with alpha-beta pruning eliminates branches t": "Alpha%E2%80%93beta_pruning",
    "Multi-head attention runs several attention functions in par": "Multi-head_attention",
    "Inverse reinforcement learning infers an unknown reward func": "Inverse_reinforcement_learning",
    "Residual learning reformulates layers to learn additive corr": "Residual_neural_network",
    "Activation functions like ReLU introduce nonlinearity so tha": "Activation_function",
    "Self-supervised learning extracts training signal from unlab": "Self-supervised_learning",
    "The perceptron convergence theorem guarantees a linear class": "Perceptron",
    "Model parallelism splits a single neural network across mult": "Model_parallelism",
    "The attention sink phenomenon shows that early tokens accumu": "Attention_(machine_learning)",
    "A just-in-time compiler translates bytecode into native mach": "Just-in-time_compilation",
    "Journaling file systems write metadata changes to a log befo": "Journaling_file_system",
    "RAID 5 stripes data across disks with distributed parity so ": "RAID",
    "Flash translation layers remap logical addresses to physical": "Flash_translation_layer",
    "SSD wear leveling distributes write operations evenly across": "Solid-state_drive",
    "Lock-free data structures use atomic compare-and-swap operat": "Non-blocking_algorithm",
    "A future represents a value that may not yet be available, l": "Futures_and_promises",
    "The actor model encapsulates state within independent actors": "Actor_model",
    "Software transactional memory groups read-write operations i": "Software_transactional_memory",
    "Compare-and-swap atomically replaces a memory value only if ": "Compare-and-swap",
    "Work-stealing schedulers let idle threads take tasks from bu": "Work_stealing",
    "Model checking exhaustively explores all reachable states of": "Model_checking",
    "Proof assistants like Coq verify mathematical theorems by ty": "Proof_assistant",
    "The Curry-Howard correspondence establishes a direct mapping": "Curry%E2%80%93Howard_correspondence",
    "SAT solvers use conflict-driven clause learning to prune the": "Boolean_satisfiability_problem",
    "The Chinese remainder theorem speeds modular arithmetic by d": "Chinese_remainder_theorem",
    "UDP provides connectionless datagram delivery with minimal o": "User_Datagram_Protocol",
    "The QUIC protocol multiplexes streams over encrypted UDP con": "QUIC",
    "BGP routers exchange reachability information between autono": "Border_Gateway_Protocol",
    "IP multicast delivers packets to a group of receivers simult": "IP_multicast",
    "Congestion control algorithms like CUBIC adjust the sending ": "TCP_congestion_control",
    "Edmonds' blossom algorithm solves maximum matching in genera": "Blossom_algorithm",
    "The min-cut max-flow theorem states that the maximum flow th": "Max-flow_min-cut_theorem",
    "Christofides' algorithm guarantees a tour within 1.5 times t": "Christofides_algorithm",
    "Reference counting frees memory immediately when an object c": "Reference_counting",
    "Mark-and-sweep garbage collection traces all reachable objec": "Tracing_garbage_collection",
    "Concurrent mark-sweep collectors reduce pause times by traci": "Concurrent_mark-sweep",
    "A copying collector compacts live objects into one half of m": "Cheney%27s_algorithm",
    "RISC architectures use fixed-length instructions and load-st": "Reduced_instruction_set_computer",
    "CISC instructions can operate directly on memory, reducing i": "Complex_instruction_set_computer",
    "SIMD instructions apply one operation to multiple data eleme": "Single_instruction,_multiple_data",
    "VLIW processors rely on the compiler to schedule independent": "Very_long_instruction_word",
    "Monads in Haskell sequence side effects by chaining computat": "Monad_(functional_programming)",
    "Continuations capture the rest of a computation as a first-c": "Continuation",
    "Rust borrow checker enforces that each value has exactly one": "Borrow_checker",
    "Hindley-Milner type inference determines the most general ty": "Hindley%E2%80%93Milner_type_system",
    "Hamming codes correct single-bit errors by placing parity bi": "Hamming_code",
    "Turbo codes approach the Shannon limit by iteratively decodi": "Turbo_code",
    "LDPC codes use sparse parity-check matrices and belief propa": "Low-density_parity-check_code",
    "Multi-version concurrency control lets readers access a cons": "Multiversion_concurrency_control",
    "LSM trees buffer writes in memory and flush sorted runs to d": "Log-structured_merge-tree",
    "Column stores compress and scan data efficiently for analyti": "Column-oriented_DBMS",
    "Query optimizers estimate plan costs using table statistics ": "Query_optimization",
    "Write-ahead log variants like ARIES use physiological loggin": "Algorithms_for_Recovery_and_Isolation_Exploiting_Semantics",
    "A covering index includes all columns a query needs so the d": "Covering_index",
    "The Shannon-Hartley theorem sets an upper bound on channel c": "Shannon%E2%80%93Hartley_theorem",
    "Zero-knowledge proofs let a prover convince a verifier that ": "Zero-knowledge_proof",
    "Side-channel attacks extract secret keys by measuring physic": "Side-channel_attack",
    "Diffie-Hellman key exchange lets two parties derive a shared": "Diffie%E2%80%93Hellman_key_exchange",
    "Certificate authorities sign digital certificates to bind a ": "Certificate_authority",
    "Elliptic curve cryptography achieves equivalent security to ": "Elliptic-curve_cryptography",
    "A message authentication code verifies both the integrity an": "Message_authentication_code",
    "Gaussian processes define a distribution over functions and ": "Gaussian_process",
    "Markov chain Monte Carlo draws correlated samples from a pos": "Markov_chain_Monte_Carlo",
    "The do-calculus provides rules for identifying causal effect": "Do-calculus",
    "Instrumental variables estimate causal effects by exploiting": "Instrumental_variables_estimation",
    "Propensity score matching balances treated and control group": "Propensity_score_matching",
    "Counterfactual reasoning asks what outcome would have occurr": "Counterfactual_thinking",
    "The backdoor criterion identifies sufficient adjustment sets": "Backdoor_criterion",
    "Message passing neural networks update each node by aggregat": "Message_passing_neural_network",
    "Graph convolutional networks generalize spatial convolutions": "Graph_neural_network",
    "Over-smoothing in deep graph networks causes node representa": "Graph_neural_network",
    "Graph-level readout functions aggregate all node embeddings ": "Graph_neural_network",
    "Natural gradient descent preconditions updates using the Fis": "Natural_gradient",
    "Demographic parity requires that a classifier's positive pre": "Fairness_(machine_learning)",
    "Calibration curves plot predicted probabilities against obse": "Calibration_(statistics)",
    "Platt scaling fits a logistic regression on model logits to ": "Platt_scaling",
    "Autoregressive models predict each time step as a function o": "Autoregressive_model",
    "State space models capture time series dynamics through late": "State-space_representation",
    "Temporal convolutional networks apply causal dilated convolu": "Temporal_convolutional_network",
    "Permutation feature importance measures how much predictive ": "Permutation_importance",
    "SHAP values assign each feature an additive contribution to ": "SHAP",
    "Partial dependence plots show the marginal effect of one or ": "Partial_dependence_plot",
    "Query-by-committee selects examples where an ensemble of mod": "Query_by_committee",
    "Expected model change selects the sample that would most alt": "Active_learning_(machine_learning)",
    "Rapidly exploring random trees build motion plans by increme": "Rapidly-exploring_random_tree",
    "Probabilistic roadmaps precompute a graph of collision-free ": "Probabilistic_roadmap",
    "Task and motion planning integrates symbolic action sequence": "Task_and_motion_planning",
    "Swarm intelligence algorithms like ant colony optimization s": "Swarm_intelligence",
    "Independent Q-learning in multi-agent settings suffers from ": "Multi-agent_reinforcement_learning",
    "Communication protocols in multi-agent reinforcement learnin": "Multi-agent_reinforcement_learning",
    "Mel spectrograms compress audio frequency bins onto the mel ": "Mel-frequency_cepstrum",
    "Speaker diarization segments an audio stream into homogeneou": "Speaker_diarisation",
    "Neural text-to-speech systems convert phoneme sequences into": "Speech_synthesis",
    "Speaker verification compares voice embeddings extracted by ": "Speaker_recognition",
    "Circuit analysis traces how specific model components compos": "Mechanistic_interpretability",
    "Sparse autoencoders decompose neural network activations int": "Sparse_dictionary_learning",
    "Reward hacking occurs when an agent exploits misspecified re": "Specification_gaming",
    "Mesa-optimization arises when a learned model internally imp": "Mesa-optimization",
    "World models learn compressed latent dynamics from raw obser": "World_model",
    "Sim-to-real transfer trains robot policies in simulation and": "Sim-to-real",
    "Domain randomization varies simulator parameters like fricti": "Domain_randomization",
    "Embodied AI systems ground language understanding in physica": "Embodied_cognition",
    "Contrastive pretraining aligns image and text embeddings in ": "Contrastive_Language-Image_Pre-training",
    "Vision-language models generate image captions by attending ": "Vision-language_model",
    "Multimodal embedding spaces enable zero-shot image classific": "Multimodal_learning",
    "Conditional random fields model label dependencies in sequen": "Conditional_random_field",
    "Energy-based models assign a scalar energy to each input-out": "Energy-based_model",
    "Function calling lets language models invoke external APIs b": "Tool_use_(AI)",
    "Planning with large language models decomposes complex goals": "Automated_planning_and_scheduling",
    "Code execution as reasoning lets agents write and run progra": "Code_generation_(AI)",
    "Agentic tool use chains multiple function calls in a loop, w": "AI_agent",
    "Chinchilla scaling shows that compute-optimal training requi": "Chinchilla_(language_model)",
    "Power law relationships link model loss to parameter count, ": "Neural_scaling_law",
    "Emergent abilities appear abruptly at certain model scales, ": "Emergence",
    "Compute-optimal training allocates a fixed compute budget by": "Neural_scaling_law",
    "Scaling laws enable researchers to predict large model perfo": "Neural_scaling_law",
    "The KV cache stores previously computed key and value tensor": "KV_cache",
    "Prefix caching reuses the KV cache of shared prompt prefixes": "KV_cache",
    "GPU tensor cores accelerate matrix multiplications by perfor": "Graphics_processing_unit",
    "TPUs use systolic arrays that pass partial sums between proc": "Tensor_Processing_Unit",
    "Memory bandwidth often bottlenecks large model training more": "Memory_bandwidth",
    "Data parallelism replicates the model across devices and par": "Data_parallelism",
    "The XLA compiler fuses sequences of elementwise operations i": "Accelerated_Linear_Algebra",
    "IEEE 754 floating point represents numbers using a sign bit,": "IEEE_754",
    "Loss scaling in mixed-precision training multiplies the loss": "Mixed-precision_training",
    "Kahan summation compensates for floating-point rounding erro": "Kahan_summation_algorithm",
    "Graphical models factorize joint distributions into local fa": "Graphical_model",
    "The Needleman-Wunsch algorithm finds a global alignment of t": "Needleman%E2%80%93Wunsch_algorithm",
    "Smith-Waterman local alignment identifies the highest-scorin": "Smith%E2%80%93Waterman_algorithm",
    "Coevolutionary analysis of multiple sequence alignments reve": "Coevolution",
    "HPC applications commonly use MPI collective operations like": "High-performance_computing",
    "Human-in-the-loop systems route low-confidence predictions t": "Human-in-the-loop",
    "The bfloat16 format keeps the same eight-bit exponent as flo": "Bfloat16_floating-point_format",
    "Gradient checkpointing trades compute for memory by recomput": "Gradient_checkpointing",
    "BLAST uses short seed matches to quickly filter candidate re": "BLAST_(biotechnology)",
    "Distributed training uses all-reduce collectives to synchron": "Distributed_computing",
    "AlphaFold2 predicts protein 3D structures from amino acid se": "AlphaFold",
    "AlphaFold2 incorporates multiple sequence alignments and str": "AlphaFold",
    "RoseTTAFold uses a three-track neural network that simultane": "RoseTTAFold",
    "Energy landscape models represent protein folding as navigat": "Protein_folding",
    "Inverse folding algorithms like ProteinMPNN design amino aci": "Protein_design",
    "AlphaFold3 extends structure prediction to complexes of prot": "AlphaFold",
    "Predicted aligned error matrices from AlphaFold2 reveal conf": "AlphaFold",
    "Enformer predicts gene expression from DNA sequence by model": "Gene_expression",
    "DeepVariant uses convolutional neural networks to call genet": "Variant_calling",
    "DNA language models like the Nucleotide Transformer learn co": "Language_model",
    "Basenji models predict cell-type-specific chromatin accessib": "Chromatin_accessibility",
    "Splicing prediction models like SpliceAI identify cryptic sp": "RNA_splicing",
    "Epigenomic imputation methods use neural networks to predict": "Epigenomics",
    "Regulatory element classifiers trained on ATAC-seq data can ": "Cis-regulatory_element",
    "Single-cell RNA sequencing analysis uses graph-based cluster": "Single-cell_sequencing",
    "Variational autoencoders like scVI model the zero-inflated c": "Variational_autoencoder",
    "RNA velocity infers future cell states by modeling the ratio": "RNA_velocity",
    "Trajectory inference algorithms like Monocle3 reconstruct ps": "Trajectory_inference",
    "Spatial transcriptomics methods combine gene expression prof": "Spatial_transcriptomics",
    "Cell type annotation transfer methods project labels from re": "Cell_type",
    "Batch correction algorithms like Harmony integrate single-ce": "Batch_effect",
    "Graph neural networks on spatial transcriptomics data model ": "Graph_neural_network",
    "ESM-2 learns protein representations by predicting masked am": "Evolutionary_scale_modeling",
    "Protein language models capture structural contacts in their": "Language_model",
    "Zero-shot mutation effect prediction scores variants by comp": "Variant_effect_predictor",
    "ESM-1v predicts the functional effects of single amino acid ": "Evolutionary_scale_modeling",
    "Evolutionary scale modeling trains transformer architectures": "Evolutionary_scale_modeling",
    "ESMFold predicts protein structures directly from single seq": "Protein_structure_prediction",
    "Protein language model embeddings cluster proteins by functi": "Language_model",
    "Fine-tuning protein language models on labeled fitness assay": "Language_model",
    "The ESM-IF1 inverse folding model generates sequences condit": "Protein_design",
    "Protein language models assign higher likelihoods to residue": "Language_model",
    "Combining protein language model embeddings with structure-b": "Enzyme_catalysis",
    "De novo molecule generation uses reinforcement learning to p": "De_novo_drug_design",
    "QSAR models map molecular descriptors to biological activity": "Quantitative_structure%E2%80%93activity_relationship",
    "ADMET prediction models estimate absorption, distribution, m": "ADMET",
    "Radiology AI detects lung nodules on chest CT scans with sen": "Computer-aided_diagnosis",
    "U-Net architectures segment tumors and organs in medical ima": "U-Net",
    "Recurrent neural networks applied to electronic health recor": "Electronic_health_record",
    "Bayesian optimization accelerates clinical trial design by a": "Bayesian_optimization",
    "Cox proportional hazards models extended with neural network": "Proportional_hazards_model",
    "Transformer models applied to longitudinal EHR sequences lea": "Electronic_health_record",
    "Causal inference methods help clinical AI distinguish treatm": "Causal_inference",
    "SMILES encodes molecular graphs as character strings, enabli": "Simplified_molecular-input_line-entry_system",
    "Graph neural networks operate directly on molecular graphs, ": "Graph_neural_network",
    "Molecular fingerprints convert chemical structures into fixe": "Chemical_fingerprint",
    "Equivariant neural networks respect rotational and translati": "Equivariant_neural_network",
    "Machine learning potentials accelerate molecular dynamics si": "Machine_learning_interatomic_potential",
    "Free energy perturbation enhanced by ML surrogate models red": "Free-energy_perturbation",
    "Neural network potentials trained on density functional theo": "Interatomic_potential",
    "Typing !! in bash repeats the entire last command, so sudo !": "Bash_(Unix_shell)",
    "The !$ shorthand expands to the last argument of the previou": "Bash_(Unix_shell)",
    "Quick substitution with ^old^new reruns the last command aft": "Bash_(Unix_shell)",
    "Pressing Ctrl-R in bash starts reverse incremental search, l": "Bash_(Unix_shell)",
    "The fc command opens your last command in your default edito": "Bash_(Unix_shell)",
    "History expansion !:2 grabs the third argument of the last c": "Bash_(Unix_shell)",
    "Using ${var:-default} expands to default when var is unset o": "Bash_(Unix_shell)",
    "The expansion ${var%.*} strips the shortest matching suffix,": "Bash_(Unix_shell)",
    "Using ${var##*/} strips the longest matching prefix through ": "Bash_(Unix_shell)",
    "The ${var//old/new} syntax performs global search-and-replac": "Bash_(Unix_shell)",
    "The expansion ${#var} returns the character length of a vari": "Bash_(Unix_shell)",
    "Indirect variable references with ${!var} expand the value o": "Bash_(Unix_shell)",
    "Process substitution with <() presents command output as a t": "Process_substitution",
    "You can redirect stderr to stdout with 2>&1, or in bash 4+ u": "Redirection_(computing)",
    "Bash can open TCP connections using /dev/tcp/host/port witho": "Bash_(Unix_shell)",
    "Here strings with <<< pass a single string as stdin to a com": "Here_document",
    "Heredocs with <<-EOF allow tab-indented content, stripping l": "Here_document",
    "Brace expansion {1..100} generates a sequence of numbers inl": "Bash_(Unix_shell)",
    "Nested brace expansion like {a,b}{1,2} produces the Cartesia": "Bash_(Unix_shell)",
    "The globstar option in bash 4+ makes **/ match directories r": "Glob_(programming)",
    "Extended globs enabled with shopt -s extglob let you write ?": "Glob_(programming)",
    "Pressing Ctrl-Z suspends the foreground process, and typing ": "Job_control_(Unix)",
    "The disown command detaches a background job from the shell ": "Job_control_(Unix)",
    "Using coproc spawns a background process with bidirectional ": "Bash_(Unix_shell)",
    "The trap command can catch signals like EXIT or ERR to run c": "Trap_(computing)",
    "The wait command blocks until all background jobs finish and": "Wait_(system_call)",
    "Using type -a instead of which shows all locations of a comm": "Bash_(Unix_shell)",
    "The command -v builtin is the POSIX-portable way to check if": "Bash_(Unix_shell)",
    "The read -r -d '' var idiom reads an entire file or stream i": "Bash_(Unix_shell)",
    "The mapfile builtin reads lines from stdin into an array var": "Bash_(Unix_shell)",
    "Using printf '%q' escapes a string for safe shell reuse, whi": "Printf_(Unix)",
    "The compgen -W builtin generates completion matches against ": "Bash_(Unix_shell)",
    "Piping through tee writes output to both a file and stdout s": "Tee_(command)",
    "Named pipes created with mkfifo act as persistent FIFO buffe": "Named_pipe",
    "Grouping commands with curly braces { cmd1; cmd2; } runs the": "Bash_(Unix_shell)",
    "Running set -euo pipefail at the top of a script makes it ex": "Bash_(Unix_shell)",
    "The shopt -s globstar option lets ** match files recursively": "Glob_(programming)",
    "Setting shopt -s nullglob makes unmatched globs expand to no": "Glob_(programming)",
    "The set -x flag prints each command with its expanded argume": "Bash_(Unix_shell)",
    "Enabling shopt -s extglob unlocks patterns like !(*.log) to ": "Glob_(programming)",
    "Declare -A in bash creates an associative array that lets yo": "Bash_(Unix_shell)",
    "The syntax ${arr[@]:2:3} slices a bash array, returning thre": "Bash_(Unix_shell)",
    "Using ${!arr[@]} expands to all the keys of a bash array, wh": "Bash_(Unix_shell)",
    "The expression ${#arr[@]} returns the number of elements in ": "Bash_(Unix_shell)",
    "Appending to a bash array with arr+=(value) avoids the need ": "Bash_(Unix_shell)",
    "Double brackets [[ ]] support regex matching with =~ and do ": "Bash_(Unix_shell)",
    "The (( )) construct in bash evaluates arithmetic expressions": "Bash_(Unix_shell)",
    "Inside [[ ]], the == operator performs glob-style pattern ma": "Bash_(Unix_shell)",
    "Bash supports a ternary-style expression with $(( condition ": "Bash_(Unix_shell)",
    "The single bracket [ is a regular command called test, so it": "Test_(Unix)",
    "The trap command with EXIT runs a cleanup function automatic": "Trap_(computing)",
    "Using trap '' SIGINT makes a script ignore interrupt signals": "Trap_(computing)",
    "A common pattern creates temp files with mktemp and register": "Trap_(computing)",
    "Trapping SIGUSR1 in a long-running script lets external proc": "Signal_(IPC)",
    "Multiple trap commands for the same signal overwrite each ot": "Trap_(computing)",
    "The exec 3>file command opens file descriptor 3 for writing,": "File_descriptor",
    "Redirecting with >&3 sends output to a previously opened fil": "File_descriptor",
    "Closing a file descriptor with exec 3>&- frees it so the und": "File_descriptor",
    "Reading from /dev/fd/N accesses file descriptor N as if it w": "File_descriptor",
    "Swapping stdout and stderr uses three steps: exec 3>&1 1>&2 ": "File_descriptor",
    "The ssh -J flag specifies a jump host, letting you reach a p": "OpenSSH",
    "SSH ControlMaster multiplexing reuses a single TCP connectio": "OpenSSH",
    "Running ssh user@host 'tar czf - /path' | tar xzf - copies a": "OpenSSH",
    "Local port forwarding with ssh -L 8080:dbhost:5432 tunnels a": "Port_forwarding",
    "The sshfs command mounts a remote filesystem over SSH so you": "SSHFS",
    "The /usr/bin/time -v command reports peak memory, page fault": "Time_(Unix)",
    "Setting TIMEFORMAT='%3R seconds' changes how the bash time k": "Bash_(Unix_shell)",
    "Adding PS4='+$(date +%s.%N) ' before set -x prefixes each tr": "Bash_(Unix_shell)",
    "GNU parallel splits input across CPU cores and runs commands": "GNU_parallel",
    "Using wait -n in bash 4.3 and later returns as soon as any b": "Bash_(Unix_shell)",
    "MapReduce processes large datasets in parallel by splitting ": "MapReduce",
    "A compiler converts high-level source code into machine inst": "Compiler",
    "Virtual memory lets processes use more address space than ph": "Virtual_memory",
    "Write-ahead logging ensures database crash recovery by recor": "Write-ahead_logging",
    "A disjoint-set data structure with union by rank and path co": "Disjoint-set_data_structure",
    "Dropout randomly deactivates neurons during training, forcin": "Dilution_(neural_networks)",
    "The softmax function converts a vector of raw logits into a ": "Softmax_function",
    "The Adam optimizer combines momentum with per-parameter adap": "Stochastic_gradient_descent#Adam",
    "One-hot encoding represents categorical variables as binary ": "One-hot",
    "The hinge loss used in SVMs penalizes predictions that fall ": "Hinge_loss",
    "The Huber loss combines squared error for small residuals wi": "Huber_loss",
    "The reparameterization trick in VAEs enables backpropagation": "Reparameterization_trick",
    "The contrastive loss pulls similar pairs closer and pushes d": "Contrastive_loss",
    "The learning rate warmup strategy starts with a small rate a": "Learning_rate",
    "The triplet loss trains embeddings by requiring an anchor to": "Triplet_loss",
    "AlphaGo combined Monte Carlo tree search with deep neural ne": "AlphaGo",
    "Beam search explores multiple candidate sequences in paralle": "Beam_search",
    "Non-maximum suppression removes redundant overlapping boundi": "Non-maximum_suppression",
    "Policy gradient methods optimize reinforcement learning poli": "Policy_gradient_methods",
    "Nucleus sampling selects tokens from the smallest set whose ": "Top-p_sampling",
    "Gradient accumulation simulates larger batch sizes by summin": "Gradient_accumulation",
    "Neural radiance fields represent 3D scenes as continuous vol": "Neural_radiance_field",
    "Transfer learning reuses features from a model trained on on": "Transfer_learning",
    "Monte Carlo dropout approximates Bayesian uncertainty by run": "Monte_Carlo_dropout",
    "Top-k sampling restricts token generation to the k highest-p": "Top-k_sampling",
    "The Miller-Rabin primality test uses modular exponentiation ": "Miller%E2%80%93Rabin_primality_test",
    "The card table in generational GC tracks old-to-young pointe": "Garbage_collection_(computer_science)",
    "Register renaming eliminates false data dependencies by mapp": "Register_renaming",
    "Lambda calculus expresses all computation using only anonymo": "Lambda_calculus",
    "Lossy compression discards perceptually irrelevant details, ": "Lossy_compression",
    "Mutual information quantifies how much knowing one random va": "Mutual_information",
    "DINO distills knowledge from a momentum teacher into a stude": "Self-supervised_learning",
    "Saddle points have zero gradient but mixed curvature, slowin": "Saddle_point",
    "The Hessian matrix captures second-order curvature informati": "Hessian_matrix",
    "CatBoost handles categorical features natively using ordered": "CatBoost",
    "Pool-based active learning selects the most informative exam": "Active_learning_(machine_learning)",
    "Stream-based active learning decides whether to label each i": "Active_learning_(machine_learning)",
    "Angular loss penalizes deviations from a target angle at the": "Metric_learning",
    "Hard negative mining focuses training on the closest incorre": "Metric_learning",
    "Multi-similarity loss jointly weighs self-similarity, positi": "Metric_learning",
    "Simultaneous localization and mapping lets a robot build a m": "Simultaneous_localization_and_mapping",
    "Temporal modeling in video networks uses three-dimensional c": "3D_convolution",
    "Program repair systems localize buggy statements and synthes": "Automatic_bug_fixing",
    "Formal specification in program synthesis constrains the sea": "Program_synthesis",
    "Execution-guided synthesis prunes candidate programs early b": "Program_synthesis",
    "Activation patching isolates causal model components by repl": "Activation_patching",
    "Scalable oversight methods like debate and recursive reward ": "AI_alignment",
    "Logic-neural integration embeds first-order logic constraint": "Neurosymbolic_AI",
    "Differentiable interpreters execute symbolic programs on neu": "Differentiable_programming",
    "Tactile sensing arrays on robotic grippers provide contact f": "Tactile_sensor",
    "Locomotion learning through deep reinforcement learning allo": "Legged_robot",
    "Continuous batching inserts new requests into a running batc": "Continuous_batching",
    "Graph-level optimization passes such as constant folding and": "Optimizing_compiler",
    "Numerical instability in softmax is avoided by subtracting t": "Softmax_function",
    "Protein structure prediction models output per-residue confi": "Protein_structure_prediction",
    "The scGPT foundation model learns cell representations from ": "Single-cell_sequencing",
    "Anomaly detection in brain MRI uses autoencoders trained on ": "Anomaly_detection",
    "Attention-gated networks highlight diagnostically relevant r": "Attention_(machine_learning)",
    "Message-passing neural networks iteratively update atom feat": "Message_passing_neural_network",
    "Binding affinity prediction models estimate the strength of ": "Binding_affinity",
    "Scoring functions trained on co-crystal structures distingui": "Scoring_functions_for_docking",
    "Contrastive learning on protein-ligand pairs improves virtua": "Virtual_screening",
    "Data augmentation artificially expands training sets by appl": "Data_augmentation",
    "Gradient descent updates model parameters by moving in the d": "Gradient_descent",
    "Feature scaling ensures that no single variable dominates th": "Feature_scaling",
    "Gradient clipping caps the norm of gradients during training": "Gradient_clipping",
    "Curriculum learning trains models on progressively harder ex": "Curriculum_learning",
    "Feature visualization optimizes an input image to maximally ": "Feature_visualization_(machine_learning)",
    "Variational inference approximates an intractable posterior ": "Variational_Bayesian_methods",
    "Bayesian optimization selects the next query point by maximi": "Bayesian_optimization",
    "Uncertainty sampling queries the instance for which the curr": "Active_learning_(machine_learning)",
    "Federated learning trains models across hospital networks wi": "Federated_learning",
    "Three-dimensional conformer generation predicts the spatial ": "Conformer_generation",
    "Extended-connectivity fingerprints encode circular substruct": "Extended-connectivity_fingerprint",
    "Digital pathology models classify tumor subtypes from whole-": "Digital_pathology",
    "Retinal fundus imaging with deep learning can detect diabeti": "Retinal_scan",
    "Biomarker discovery pipelines use gradient-based feature att": "Biomarker_discovery",
    "Interaction fingerprints encode hydrogen bonds, salt bridges": "Molecular_descriptor",
}


def _extract_subject(sentence):
    """Extract the main subject from a sentence for Wikipedia lookup."""
    s = sentence.strip()

    # Check overrides first (match on longest prefix)
    best_match = None
    for key, article in WIKI_OVERRIDES.items():
        if s.startswith(key):
            if best_match is None or len(key) > len(best_match[0]):
                best_match = (key, article)
    if best_match:
        return best_match[1]

    # Pattern: "The X algorithm/theorem/problem/protocol/equation ..."
    m = re.match(
        r"^The\s+(.+?)\s+(?:algorithm|theorem|problem|protocol|architecture|"
        r"equation|hypothesis|method|formula|phenomenon|correspondence|criterion)\b", s)
    if m:
        return m.group(1).replace(" ", "_")

    # Pattern: "X's algorithm/law/theorem ..."
    m = re.match(r"^(\w+(?:['’]s)?)\s+(algorithm|theorem|law|rule)\b", s)
    if m:
        return f"{m.group(1)}_{m.group(2)}"

    # Pattern: "A/An X ..." where X is a data structure / concept
    m = re.match(
        r"^An?\s+(.+?)\s+(?:is|achieves|stores|uses|lets|keeps|builds|finds|"
        r"guarantees|represents|provides|evicts|signals|detects|verifies)\b", s)
    if m:
        subj = m.group(1)
        if len(subj.split()) <= 5:
            return subj.replace(" ", "_")

    # Pattern: named thing at start (capitalized / hyphenated words)
    m = re.match(
        r"^([A-Z][\w’'-]+(?:\s+[A-Za-z][\w’'-]+){0,4})\s+"
        r"(?:is|are|uses?|lets?|finds?|builds?|tracks?|splits?|maps?|creates?|"
        r"converts?|computes?|predicts?|generates?|combines?|exploits?|estimates?|"
        r"measures?|enables?|provides?|reduces?|assigns?|updates?|trains?|learns?|"
        r"models?|encodes?|applies?|extends?|incorporates?|outputs?|defines?|"
        r"replaces?|captures?|achieves?|stabilizes?|guarantees?|minimizes?|"
        r"simplif(?:y|ies)|requires?|constrains?|routes?|detects?|classif(?:y|ies)|"
        r"segments?|compress(?:es)?|infers?|reconstruct|projects?|integrat(?:e|es)|"
        r"predicts?|operates?|select|accelerat(?:e|es)|adapts?|opens?|reads?|"
        r"runs?|distribut(?:e|es)|divid(?:e|es)|strips?|expands?|starts?)\b", s)
    if m:
        return m.group(1).replace(" ", "_")

    # Fallback: take words until a common verb
    stop = {'is', 'are', 'uses', 'lets', 'finds', 'builds', 'can', 'does',
            'achieves', 'stores', 'keeps', 'guarantees', 'predicts', 'has',
            'computes', 'in', 'by', 'with', 'that', 'the', 'a', 'an',
            'updates', 'trains', 'generates', 'combines', 'exploits',
            'estimates', 'measures', 'reduces', 'allows', 'provides',
            'makes', 'opens', 'runs', 'sets', 'shows', 'adds'}
    words = s.split()
    subj_words = []
    for w in words[:6]:
        if w.lower() in stop:
            break
        subj_words.append(w)
    if subj_words:
        return "_".join(subj_words).rstrip(",.")

    return words[0]


def get_wiki_url(sentence):
    """Get a Wikipedia URL for the given sentence's topic."""
    article = _extract_subject(sentence)
    article = article.replace(" ", "_")
    return f"https://en.wikipedia.org/wiki/{article}"


_SIGNING_KEY = os.environ.get("TYPEFACT_SECRET", "change-me-before-deploying").encode()


def _sign_payload(payload_bytes):
    return hmac.new(_SIGNING_KEY, payload_bytes, hashlib.sha256).hexdigest()


def _verify_payload(payload_bytes, signature):
    expected = _sign_payload(payload_bytes)
    return hmac.compare_digest(expected, signature)


def export_results(candidate, rounds, out_dir="."):
    """Write signed JSON results to disk. Returns the filename."""
    payload = {
        "candidate": candidate,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "rounds": rounds,
    }
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    signature = _sign_payload(payload_bytes)
    envelope = {"payload": payload, "signature": signature}

    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", candidate)
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"results_{safe_name}_{ts}.json"
    filepath = os.path.join(out_dir, filename)
    with open(filepath, "w") as f:
        json.dump(envelope, f, indent=2)
    return filepath


def verify_results_file(path):
    """Verify the signature of an exported results file. Returns (ok, payload)."""
    with open(path) as f:
        envelope = json.load(f)
    payload = envelope["payload"]
    signature = envelope["signature"]
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ok = _verify_payload(payload_bytes, signature)
    return ok, payload


def get_candidate_name(stdscr):
    """Prompt for candidate name using curses. Returns the name string."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    mid_y = h // 2 - 2
    draw_centered(stdscr, mid_y, "═══  SCREENING MODE  ═══",
                  curses.color_pair(1) | curses.A_BOLD)
    draw_centered(stdscr, mid_y + 2, "Enter your name:", curses.color_pair(3))

    curses.curs_set(1)
    curses.echo()
    name_x = max(0, (w - 40) // 2)
    stdscr.move(mid_y + 4, name_x)
    stdscr.clrtoeol()
    name = stdscr.getstr(mid_y + 4, name_x, 40).decode("utf-8", errors="replace").strip()
    curses.noecho()
    curses.curs_set(0)
    return name if name else "anonymous"


TITLE_ART = r"""
  ______                   ______          __
 /_  __/_  ______  ___    / ____/___ ___  / /_
  / / / / / / __ \/ _ \  / /_  / __ `/ / / __/
 / / / /_/ / /_/ /  __/ / __/ / /_/ / /_/ /_
/_/  \__, / .___/\___/ /_/    \__,_/\___\__/
    /____/_/
"""


def draw_centered(win, y, text, attr=0, max_width=None):
    h, w = win.getmaxyx()
    if max_width:
        w = min(w, max_width)
    x = max(0, (w - len(text)) // 2)
    try:
        win.addstr(y, x, text[:w - 1], attr)
    except curses.error:
        pass


def show_title_screen(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    lines = TITLE_ART.strip('\n').split('\n')
    start_y = max(0, h // 2 - len(lines) // 2 - 4)
    for i, line in enumerate(lines):
        draw_centered(stdscr, start_y + i, line, curses.color_pair(1) | curses.A_BOLD)

    tag_y = start_y + len(lines) + 1
    draw_centered(stdscr, tag_y, "CS  •  ML  •  AI  •  SCREENING", curses.color_pair(3))
    draw_centered(stdscr, tag_y + 2, "Type the facts as fast as you can!", curses.color_pair(2))
    draw_centered(stdscr, tag_y + 3, "Results will be signed and exported.", curses.color_pair(2) | curses.A_DIM)
    draw_centered(stdscr, tag_y + 5, "Press any key to start  •  'q' to quit", curses.A_DIM)

    stdscr.refresh()
    key = stdscr.getch()
    return key != ord('q')


def show_results(stdscr, results):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)

    y = max(1, h // 2 - len(results) - 4)
    draw_centered(stdscr, y, "═══  SESSION RESULTS  ═══", curses.color_pair(4) | curses.A_BOLD)
    y += 2

    total_wpm = 0
    total_acc = 0
    for i, r in enumerate(results):
        total_wpm += r['wpm']
        total_acc += r['accuracy']
        line = f"Round {i+1}:  {r['wpm']:5.1f} WPM  |  {r['accuracy']:5.1f}% accuracy"
        draw_centered(stdscr, y, line, curses.color_pair(5))
        y += 1

    y += 1
    n = len(results)
    avg_wpm = total_wpm / n
    avg_acc = total_acc / n
    draw_centered(stdscr, y, f"Average:  {avg_wpm:.1f} WPM  |  {avg_acc:.1f}% accuracy",
                  curses.color_pair(3) | curses.A_BOLD)
    y += 2
    draw_centered(stdscr, y, "Press any key to return to title  •  'q' to quit", curses.A_DIM)
    stdscr.refresh()
    return stdscr.getch() != ord('q')


def build_display_lines(sentence, width):
    """Wrap sentence and return (lines, char_to_row_col) mapping each sentence
    index to a (row, col) on screen. Spaces at line breaks become the first
    char of the next line — no characters are lost or reordered."""
    lines = []
    mapping = {}
    row = col = 0
    current_line = []

    for i, ch in enumerate(sentence):
        if col >= width and ch == ' ':
            lines.append(''.join(current_line))
            current_line = []
            row += 1
            col = 0
        if col >= width:
            # mid-word break
            lines.append(''.join(current_line))
            current_line = []
            row += 1
            col = 0
        mapping[i] = (row, col)
        current_line.append(ch)
        col += 1

    if current_line:
        lines.append(''.join(current_line))

    return lines, mapping


def run_round(stdscr, sentence):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    text_width = min(w - 4, 90)
    lines, mapping = build_display_lines(sentence, text_width)

    curses.init_pair(6, curses.COLOR_GREEN, -1)    # correct
    curses.init_pair(7, curses.COLOR_RED, -1)      # wrong
    curses.init_pair(8, curses.COLOR_WHITE, -1)    # untyped
    curses.init_pair(9, curses.COLOR_YELLOW, -1)   # cursor
    curses.init_pair(10, curses.COLOR_CYAN, -1)    # stats

    typed = []
    keystrokes = []
    start_time = None

    stdscr.nodelay(False)
    stdscr.timeout(-1)

    while True:
        stdscr.erase()
        pos = len(typed)

        draw_centered(stdscr, 1, "Type the text below  •  Esc to skip", curses.A_DIM)

        text_start_y = max(3, h // 2 - len(lines))
        x_offset = max(0, (w - text_width) // 2)

        for i, ch in enumerate(sentence):
            row, col = mapping[i]
            if i < pos:
                if typed[i] == ch:
                    attr = curses.color_pair(6) | curses.A_BOLD
                else:
                    attr = curses.color_pair(7) | curses.A_BOLD | curses.A_UNDERLINE
            elif i == pos:
                attr = curses.color_pair(9) | curses.A_REVERSE
            else:
                attr = curses.color_pair(8) | curses.A_DIM
            try:
                stdscr.addch(text_start_y + row, x_offset + col, ch, attr)
            except curses.error:
                pass

        # Progress bar
        progress = pos / len(sentence) if sentence else 0
        bar_width = min(40, text_width)
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        bar_y = text_start_y + len(lines) + 2
        draw_centered(stdscr, bar_y, f"[{bar}] {progress * 100:.0f}%", curses.color_pair(10))

        # Live stats
        if start_time and pos > 0:
            elapsed = time.time() - start_time
            wpm = (pos / 5) / (elapsed / 60) if elapsed > 0 else 0
            correct = sum(1 for i, c in enumerate(typed) if c == sentence[i])
            acc = (correct / pos) * 100
            stats_y = bar_y + 2
            draw_centered(stdscr, stats_y, f"{wpm:.0f} WPM  •  {acc:.0f}% accuracy", curses.color_pair(10))

        stdscr.refresh()

        if pos >= len(sentence):
            break

        key = stdscr.getch()

        if key == 27:  # Esc
            return None

        if key in (curses.KEY_BACKSPACE, 127, 8):
            if typed:
                typed.pop()
                keystrokes.append({"t": time.time(), "k": "BS"})
            continue

        if key == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            text_width = min(w - 4, 90)
            lines, mapping = build_display_lines(sentence, text_width)
            continue

        if key < 32 or key > 126:
            continue

        if start_time is None:
            start_time = time.time()

        typed.append(chr(key))
        keystrokes.append({"t": time.time(), "k": chr(key)})

    elapsed = time.time() - start_time if start_time else 1
    wpm = (len(sentence) / 5) / (elapsed / 60) if elapsed > 0 else 0
    correct = sum(1 for i, c in enumerate(typed) if i < len(sentence) and c == sentence[i])
    accuracy = (correct / len(sentence)) * 100

    bar_y = text_start_y + len(lines) + 2
    draw_centered(stdscr, bar_y + 4, "Done!  Press any key to continue  •  L to learn more",
                  curses.color_pair(6) | curses.A_BOLD)

    url = get_wiki_url(sentence)
    short_url = url.replace("https://en.wikipedia.org/wiki/", "wiki: ")
    draw_centered(stdscr, bar_y + 6, short_url, curses.A_DIM)

    stdscr.refresh()
    key = stdscr.getch()
    if key in (ord('l'), ord('L')):
        curses.endwin()
        webbrowser.open(url)
        curses.doupdate()
        stdscr.refresh()

    intervals = []
    for i in range(1, len(keystrokes)):
        intervals.append(round(keystrokes[i]["t"] - keystrokes[i - 1]["t"], 4))

    relative_keystrokes = [{"t": round(ks["t"] - start_time, 4), "k": ks["k"]}
                           for ks in keystrokes] if start_time else keystrokes

    return {
        'sentence': sentence,
        'wpm': round(wpm, 2),
        'accuracy': round(accuracy, 2),
        'elapsed': round(elapsed, 3),
        'keystrokes': relative_keystrokes,
        'inter_key_intervals': intervals,
    }


def show_export_screen(stdscr, filepath):
    """Show the export confirmation screen."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)

    mid_y = h // 2 - 3
    draw_centered(stdscr, mid_y, "═══  RESULTS EXPORTED  ═══",
                  curses.color_pair(4) | curses.A_BOLD)
    draw_centered(stdscr, mid_y + 2, "Signed results saved to:",
                  curses.color_pair(3))
    draw_centered(stdscr, mid_y + 4, filepath,
                  curses.color_pair(2) | curses.A_BOLD)
    draw_centered(stdscr, mid_y + 6, "Submit this file to your reviewer.",
                  curses.A_DIM)
    draw_centered(stdscr, mid_y + 8, "Press any key to continue", curses.A_DIM)
    stdscr.refresh()
    stdscr.getch()


def main(stdscr):
    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.keypad(True)

    candidate = get_candidate_name(stdscr)

    while True:
        if not show_title_screen(stdscr):
            break

        pool = random.sample(SENTENCES, min(10, len(SENTENCES)))
        results = []

        for sentence in pool:
            result = run_round(stdscr, sentence)
            if result is None:  # skipped
                continue
            results.append(result)

        if results:
            display_results = [{'wpm': r['wpm'], 'accuracy': r['accuracy']}
                               for r in results]
            if not show_results(stdscr, display_results):
                filepath = export_results(candidate, results)
                show_export_screen(stdscr, filepath)
                break
            filepath = export_results(candidate, results)
            show_export_screen(stdscr, filepath)
        else:
            break


def cli_verify(path):
    """CLI verification of a results file."""
    try:
        ok, payload = verify_results_file(path)
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Error reading {path}: {e}")
        sys.exit(1)

    candidate = payload.get("candidate", "?")
    timestamp = payload.get("timestamp", "?")
    rounds = payload.get("rounds", [])

    if ok:
        print(f"\033[32m✓ SIGNATURE VALID\033[0m")
    else:
        print(f"\033[31m✗ SIGNATURE INVALID — results may have been tampered with\033[0m")

    print(f"  Candidate : {candidate}")
    print(f"  Timestamp : {timestamp}")
    print(f"  Rounds    : {len(rounds)}")
    print()

    total_wpm = 0
    total_acc = 0
    for i, r in enumerate(rounds):
        wpm = r.get("wpm", 0)
        acc = r.get("accuracy", 0)
        total_wpm += wpm
        total_acc += acc
        intervals = r.get("inter_key_intervals", [])
        if intervals:
            avg_iki = sum(intervals) / len(intervals)
            std_iki = (sum((x - avg_iki) ** 2 for x in intervals) / len(intervals)) ** 0.5
            iki_str = f"avg IKI {avg_iki * 1000:.0f}ms  σ {std_iki * 1000:.0f}ms"
        else:
            iki_str = "no keystroke data"
        sentence = r.get("sentence", "")
        preview = sentence[:60] + "..." if len(sentence) > 60 else sentence
        print(f"  Round {i + 1:2d}: {wpm:5.1f} WPM | {acc:5.1f}% | {iki_str}")
        print(f"           {preview}")

    if rounds:
        n = len(rounds)
        print(f"\n  Average : {total_wpm / n:.1f} WPM | {total_acc / n:.1f}%")

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Terminal typing game — screening edition")
    parser.add_argument("--verify", metavar="FILE",
                        help="Verify a signed results file instead of playing")
    args = parser.parse_args()

    if args.verify:
        cli_verify(args.verify)
    else:
        curses.wrapper(main)
