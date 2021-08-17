#! python3

# Definition of used DB blocks

# Syntax per row:
#   BYTE_ADDRESS    VARIABLE_NAME     TYPE    # COMMENT

db99_layout = '''
0	Voorspelling_uur[0].Kwartier[0]	REAL
4	Voorspelling_uur[0].Kwartier[1]	REAL
8	Voorspelling_uur[0].Kwartier[2]	REAL
12	Voorspelling_uur[0].Kwartier[3]	REAL
16	Voorspelling_uur[1].Kwartier[0]	REAL
20	Voorspelling_uur[1].Kwartier[1]	REAL
24	Voorspelling_uur[1].Kwartier[2]	REAL
28	Voorspelling_uur[1].Kwartier[3]	REAL
32	Voorspelling_uur[2].Kwartier[0]	REAL
36	Voorspelling_uur[2].Kwartier[1]	REAL
40	Voorspelling_uur[2].Kwartier[2]	REAL
44	Voorspelling_uur[2].Kwartier[3]	REAL
48	Voorspelling_uur[3].Kwartier[0]	REAL
52	Voorspelling_uur[3].Kwartier[1]	REAL
56	Voorspelling_uur[3].Kwartier[2]	REAL
60	Voorspelling_uur[3].Kwartier[3]	REAL
64	Voorspelling_uur[4].Kwartier[0]	REAL
68	Voorspelling_uur[4].Kwartier[1]	REAL
72	Voorspelling_uur[4].Kwartier[2]	REAL
76	Voorspelling_uur[4].Kwartier[3]	REAL
80	Voorspelling_uur[5].Kwartier[0]	REAL
84	Voorspelling_uur[5].Kwartier[1]	REAL
88	Voorspelling_uur[5].Kwartier[2]	REAL
92	Voorspelling_uur[5].Kwartier[3]	REAL
96	Voorspelling_uur[6].Kwartier[0]	REAL
100	Voorspelling_uur[6].Kwartier[1]	REAL
104	Voorspelling_uur[6].Kwartier[2]	REAL
108	Voorspelling_uur[6].Kwartier[3]	REAL
112	Voorspelling_uur[7].Kwartier[0]	REAL
116	Voorspelling_uur[7].Kwartier[1]	REAL
120	Voorspelling_uur[7].Kwartier[2]	REAL
124	Voorspelling_uur[7].Kwartier[3]	REAL
128	Voorspelling_uur[8].Kwartier[0]	REAL
132	Voorspelling_uur[8].Kwartier[1]	REAL
136	Voorspelling_uur[8].Kwartier[2]	REAL
140	Voorspelling_uur[8].Kwartier[3]	REAL
144	Voorspelling_uur[9].Kwartier[0]	REAL
148	Voorspelling_uur[9].Kwartier[1]	REAL
152	Voorspelling_uur[9].Kwartier[2]	REAL
156	Voorspelling_uur[9].Kwartier[3]	REAL
160	Voorspelling_uur[10].Kwartier[0]	REAL
164	Voorspelling_uur[10].Kwartier[1]	REAL
168	Voorspelling_uur[10].Kwartier[2]	REAL
172	Voorspelling_uur[10].Kwartier[3]	REAL
176	Voorspelling_uur[11].Kwartier[0]	REAL
180	Voorspelling_uur[11].Kwartier[1]	REAL
184	Voorspelling_uur[11].Kwartier[2]	REAL
188	Voorspelling_uur[11].Kwartier[3]	REAL
192	Voorspelling_uur[12].Kwartier[0]	REAL
196	Voorspelling_uur[12].Kwartier[1]	REAL
200	Voorspelling_uur[12].Kwartier[2]	REAL
204	Voorspelling_uur[12].Kwartier[3]	REAL
208	Voorspelling_uur[13].Kwartier[0]	REAL
212	Voorspelling_uur[13].Kwartier[1]	REAL
216	Voorspelling_uur[13].Kwartier[2]	REAL
220	Voorspelling_uur[13].Kwartier[3]	REAL
224	Voorspelling_uur[14].Kwartier[0]	REAL
228	Voorspelling_uur[14].Kwartier[1]	REAL
232	Voorspelling_uur[14].Kwartier[2]	REAL
236	Voorspelling_uur[14].Kwartier[3]	REAL
240	Voorspelling_uur[15].Kwartier[0]	REAL
244	Voorspelling_uur[15].Kwartier[1]	REAL
248	Voorspelling_uur[15].Kwartier[2]	REAL
252	Voorspelling_uur[15].Kwartier[3]	REAL
256	Voorspelling_uur[16].Kwartier[0]	REAL
260	Voorspelling_uur[16].Kwartier[1]	REAL
264	Voorspelling_uur[16].Kwartier[2]	REAL
268	Voorspelling_uur[16].Kwartier[3]	REAL
272	Voorspelling_uur[17].Kwartier[0]	REAL
276	Voorspelling_uur[17].Kwartier[1]	REAL
280	Voorspelling_uur[17].Kwartier[2]	REAL
284	Voorspelling_uur[17].Kwartier[3]	REAL
288	Voorspelling_uur[18].Kwartier[0]	REAL
292	Voorspelling_uur[18].Kwartier[1]	REAL
296	Voorspelling_uur[18].Kwartier[2]	REAL
300	Voorspelling_uur[18].Kwartier[3]	REAL
304	Voorspelling_uur[19].Kwartier[0]	REAL
308	Voorspelling_uur[19].Kwartier[1]	REAL
312	Voorspelling_uur[19].Kwartier[2]	REAL
316	Voorspelling_uur[19].Kwartier[3]	REAL
320	Voorspelling_uur[20].Kwartier[0]	REAL
324	Voorspelling_uur[20].Kwartier[1]	REAL
328	Voorspelling_uur[20].Kwartier[2]	REAL
332	Voorspelling_uur[20].Kwartier[3]	REAL
336	Voorspelling_uur[21].Kwartier[0]	REAL
340	Voorspelling_uur[21].Kwartier[1]	REAL
344	Voorspelling_uur[21].Kwartier[2]	REAL
348	Voorspelling_uur[21].Kwartier[3]	REAL
352	Voorspelling_uur[22].Kwartier[0]	REAL
356	Voorspelling_uur[22].Kwartier[1]	REAL
360	Voorspelling_uur[22].Kwartier[2]	REAL
364	Voorspelling_uur[22].Kwartier[3]	REAL
368	Voorspelling_uur[23].Kwartier[0]	REAL
372	Voorspelling_uur[23].Kwartier[1]	REAL
376	Voorspelling_uur[23].Kwartier[2]	REAL
380	Voorspelling_uur[23].Kwartier[3]	REAL
384	Ochtend	TIME	# in milliseconden vanaf middernacht
388	Sunrise	TIME	# in milliseconden vanaf middernacht
392	Sunset	TIME	# in milliseconden vanaf middernacht
396	Nacht	TIME	# in milliseconden vanaf middernacht
400	BYD.Charge_Discharge	REAL	# + = charge; - = discharge
404	BYD.SOC	REAL
408	BYD.SOH	REAL
412	BYD.Capacity	REAL
420	PowerFlow.Grid	REAL	# + = verbruik vanaf grid; - = teruglevering aan grid
424	PowerFlow.House	REAL
428	PowerFlow.Solar	REAL
440	TimeStamp	TIME	# in milliseconden vanaf middernacht
444	Optimizers	INT
'''
