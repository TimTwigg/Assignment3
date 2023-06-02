from src.config import Config

class PageRanker:
    def __init__(self):
        """Compute the PageRank for a dataset."""
        self.config = Config()
    
    def run(self, links: dict[int: list[set[int], int]]) -> dict[int: float]:
        """Compute PageRank.
        
        Args:
            links (dict[int: list[set[int], int]]): the extracted links corpus of incoming links to each page and the number of outgoing links.
        """
        pageranks: dict[int: float] = {id: 1 for id in links.keys()}
        old: dict[int: float] = {}
        
        # calculate new page rank
        def pr(i):
            nonlocal old, links
            s = 0
            for j in links[i][0]:
                s += old[j]/links[j][1]
            return (1-self.config.pageRank_damping_factor) + self.config.pageRank_damping_factor * s
        
        # max iterations
        iters = len(links)
        if self.config.pageRank_max_iters > 0:
            iters = min(iters, self.config.pageRank_max_iters)
        
        for _ in range(iters):
            # update old
            old = dict(pageranks)
            # calculate pr for each page
            for page in pageranks.keys():
                pageranks[page] = pr(page)
        
        total = sum(pageranks.values())
        for page,rank in pageranks.items():
            pageranks[page] = rank/total
        return pageranks