# R07 pre-main seed-range correction

Static review before main controls/actual found that original main bootstrap seeds481000+1000*c+i overlapped the next main control's generation seed, and real seeds490000+i overlapped control10. No main control or actual panel had been executed. Preserve initial card/pilot snapshot; replace only main null seeds with500000+1000*c+i and realnull seeds with520000+i. Main control seeds remain480000+1000*c (generation consumesseed+1); pilot seeds unchanged. These three main ranges are now disjoint. No model, statistic, cutoff, scope or real-outcome-dependent choice changed.

Pilot used60panels in2.134s: full-echo29/29mapping and100%heldmatches;25%-echo29/29mapping and27.09%heldmatches; both19-null floor.05; ordinarytail1.00. Forecast1600finalpanels about57seconds. ConditionalMLE qualification gates all passed. Main controls proceed before realmeasurement.
