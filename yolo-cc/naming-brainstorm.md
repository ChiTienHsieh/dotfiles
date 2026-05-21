# CLI Tool Naming Brainstorm

## Recommendation

Current working name: **yolo-cc**.

Why:

- Already matches the repo/tool concept.
- Memorable and CLI-friendly.
- Honest about the "let Claude Code run with more autonomy" intent without sounding like a security product.
- Easy to type, grep, document, and turn into a binary name.

Strong alternates:

- **airlock**: best if the positioning becomes "safe boundary for risky AI work".
- **cc-cage**: clear, short, and describes containment, but feels more like a wrapper than a product.
- **cage**: very CLI-friendly, but too generic unless paired with strong docs.
- **offleash**: captures autonomy well, but may sound too risky for public docs.

Avoid for now:

- **nuke**, **rampage**, **rogue**, **feral**, **quarantine**: memorable, but they make the tool sound more dangerous than useful.
- **claud-safe**, **dockerclaude**, **claudebox**: too tied to Claude or Docker if the tool later supports other agents/runtimes.
- **sentinel**, **aegis**, **bastion**, **citadel**: polished, but they imply enterprise security posture we probably do not want to promise.

Naming criteria:

- 2-12 chars for the executable is ideal.
- Should make sense in commands like `yolo-cc run`, `yolo-cc shell`, and `yolo-cc doctor`.
- Should not imply perfect sandboxing/security unless the implementation actually earns that claim.
- Should be easy to say out loud without making the maintainer regret several life choices.

## Category 1: Safety / Isolation / Containment

1. cage
2. vault
3. bulkhead
4. airlock
5. quarantine
6. padded
7. bunker
8. cocoon
9. capsule
10. shell
11. moat
12. ward
13. fenced
14. cloister
15. hutch
16. terrarium
17. bubble
18. safehouse
19. ark
20. rampart

## Category 2: Autonomy / Freedom / Unleashing

21. unleash
22. autopilot
23. feral
24. untether
25. roam
26. rampage
27. prowl
28. loose
29. wildrun
30. offleash
31. freeroam
32. unchain
33. drift
34. cruise
35. gallivant
36. stampede
37. maverick
38. rogue
39. stray
40. nomad

## Category 3: Wordplay on YOLO / Claude / AI / Containers

41. yolo-cc
42. clauge
43. claud-safe
44. yolode
45. dockerclaude
46. clontainer
47. clowd
48. claudebox
49. yolai
50. clawde
51. airlclaude
52. clauderun
53. yolocode
54. runclaude
55. claudelet
56. clodock
57. clsafe
58. ycc
59. claiguard
60. claudeloop

## Category 4: Short Punchy CLI-Friendly (2-8 chars)

61. cask
62. brig
63. pen
64. hold
65. den
66. hive
67. bolt
68. orb
69. silo
70. plex
71. grit
72. tusk
73. rax
74. vox
75. jinx
76. hex
77. nuke
78. flux
79. zap
80. dojo

## Category 5: Sci-Fi Inspired

81. holodeck
82. nexus
83. cortex
84. genesis
85. aegis
86. sentinel
87. bastion
88. citadel
89. cradle
90. monolith
91. obelisk
92. prism
93. phantom
94. replicant
95. construct

## Category 6: Compound Names (claude-X, cc-X, X-cc)

96. cc-cage
97. cc-loose
98. claude-pen
99. cc-yolo
100. cc-wild
