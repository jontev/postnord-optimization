# postnord-optimization
- Repository from project in optimization (operations research).
- Project was to model and optimize transportation inside a newly built warehouse for a swedish postal service company.
- More specifically, first how to near optimally book trailers and trucks for transportation of that days goods
- then decide where they would park and how goods would be transported inside the warehouse
- Was solved on a daily basis.
- First a mathematical model (Integer programming model) was defined, see picture
- then the problem was decomposed into the well known transportation problem 
- then different metaheuristics were implemented and evaluated, by comparing them to the solution generated by the gurobi solver.
- Four metaheuristics were implemented, taboo search, local search, simulated annealing and variable neighbourhood search.
- SA and VNS were determined to be the best, and good solutions were generated within a reasonable amount of time using them
- Code is not runnable due to classified data
![Screenshot 2022-02-15 at 19-17-32 CDIO - Dokumentation](https://user-images.githubusercontent.com/98525050/154124050-02ec1f12-89b0-4d63-9853-2cffee64ade8.png)
