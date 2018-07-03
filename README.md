# Model-free video game personalization for educational serious games

This project applies reinforcement learning in order to dynamically modify a serious game environment to help the player achieve a certain learning objective. This project has grown closely with our case study of an [archaeological educational serious game](http://www.iiia.csic.es/draga/downloads.html) based in [la Draga](http://www.iiia.csic.es/draga/).

## Abstract

This MSc final project focuses on the problem of reconciling the fun aspect of an educational serious video game with its learning objective. For this, we propose bringing video game personalization to educational serious games in order to help players achieve their learning objectives by modifying the game environment dynamically in response to the player's behavior. Most applications of video game personalization, however, require detailed models of the player using a lot of information that is often not practical or even possible to get from them.

Even though reinforcement learning in the field of video games has mainly been used for playing, we believe that it is a valuable tool which we will use to achieve an adaptive environment without needing a model of the player. Specifically, we will use the Q-Learning technique to train an AI to help simulated players with simple behaviors fulfill learning objectives in a simplified version of the game.

With our case study, a virtual reality archaeological educational serious game, we collected a lot of data and obtained insight into this problem. First, this project studies this data to then try to clearly formalize the problem and decide an appropriate approach. We will also use this data to cluster our players into four types to use for the simulations of different players.

Lastly, we turn our attention in a way to evaluate the policies obtained from training and visualize them to better understand what was learned. We will also propose the best course of action when we do not yet know what type of player we are dealing with in a particular playthrough.

#### [Thesis](https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games/blob/master/Thesis/thesis.pdf)

## Implemented tricks and techniques

> - Irace
> - Q-Learning
> - K-Means clustering
> - Player simulation
> - State and action space discretization

## Implemented visualization functionalities

> - ipywidgeds
> - Q-Matrix heatmap visualization
> - Unity 3D visualization of gameplays in the form of 3D heatmaps.

## Notebooks

#### [Draga 2D representation example as ipywidget using HTML](https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games/blob/master/Code/Draga.ipynb)

#### [Gameplay logs analysis and clustering](https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games/blob/master/Code/Logs%20and%20data%20analysis.ipynb)

#### [Training and game visualization](https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games/blob/master/Code/game_learning.ipynb)

#### [Inspection and visualization of learned Q-Matrices](https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games/blob/master/Code/Q%20inspection.ipynb)

#### [Evaluation and relative evaluation of policies](https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games/blob/master/Code/learning_evaluation.ipynb)

### BibTex reference format for citation for the report of the Master's Thesis

```
@misc{AESGCebrianThesis,
title={Model-free video game personalization for educational serious games},
url={https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games/blob/master/Thesis/thesis.pdf},
author={Cebrián, Sergi},
  year={2018}
}
```

### BibTex reference format for citation for the Code
```
@misc{AESGCebrian,
title={Model-free video game personalization for educational serious games},
url={https://github.com/SergiCebrianGres/Model-free-video-game-personalization-for-educational-serious-games},
author={Cebrián, Sergi},
  year={2018}
}
```