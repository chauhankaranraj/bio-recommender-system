import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

/**
 * D3 force-directed bipartite network graph.
 *
 * Props:
 *   data    : { nodes: [{id, type, label, degree}], links: [{source, target}] }
 *   width   : number (default 800)
 *   height  : number (default 500)
 */
export default function NetworkGraph({ data, width = 800, height = 500 }) {
  const svgRef = useRef(null)

  useEffect(() => {
    if (!data || !data.nodes.length) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    // ── Zoom layer ────────────────────────────────────────────────────────────
    const zoom = d3.zoom()
      .scaleExtent([0.3, 4])
      .on('zoom', (e) => g.attr('transform', e.transform))

    svg.call(zoom)

    const g = svg.append('g')

    // ── Force simulation ──────────────────────────────────────────────────────
    const simulation = d3.forceSimulation(data.nodes)
      .force('link',   d3.forceLink(data.links).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-180))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(22))

    // ── Links ─────────────────────────────────────────────────────────────────
    const link = g.append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('class', 'link')
      .attr('stroke-width', 1.5)

    // ── Nodes ─────────────────────────────────────────────────────────────────
    const node = g.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', d => Math.max(8, Math.min(20, 6 + d.degree * 1.5)))
      .attr('class', d => d.type === 'gene' ? 'node-gene' : 'node-disease')
      .style('cursor', 'grab')
      .call(
        d3.drag()
          .on('start', (e, d) => {
            if (!e.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x; d.fy = d.y
          })
          .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
          .on('end',  (e, d) => {
            if (!e.active) simulation.alphaTarget(0)
            d.fx = null; d.fy = null
          })
      )

    // ── Labels ────────────────────────────────────────────────────────────────
    const label = g.append('g')
      .selectAll('text')
      .data(data.nodes)
      .join('text')
      .attr('class', 'node-label')
      .attr('dy', '0.35em')
      .attr('dx', d => Math.max(8, Math.min(20, 6 + d.degree * 1.5)) + 4)
      .text(d => d.label.length > 20 ? d.label.slice(0, 18) + '…' : d.label)

    // ── Tooltip ───────────────────────────────────────────────────────────────
    const tooltip = d3.select('body')
      .append('div')
      .style('position', 'absolute')
      .style('background', '#1a2340')
      .style('border', '1px solid #2a3560')
      .style('border-radius', '8px')
      .style('padding', '8px 12px')
      .style('font-size', '12px')
      .style('color', '#e2e8f0')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', 9999)

    node
      .on('mouseover', (e, d) => {
        tooltip
          .html(`<strong>${d.label}</strong><br/>${d.type} · degree ${d.degree}`)
          .style('opacity', 1)
      })
      .on('mousemove', (e) => {
        tooltip
          .style('left', (e.pageX + 14) + 'px')
          .style('top',  (e.pageY - 28) + 'px')
      })
      .on('mouseout', () => tooltip.style('opacity', 0))

    // ── Tick ──────────────────────────────────────────────────────────────────
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y)
    })

    // ── Legend ────────────────────────────────────────────────────────────────
    const legend = svg.append('g').attr('transform', 'translate(16,16)')
    ;[
      { label: 'Gene',    color: '#2993fa', stroke: '#52b4fd' },
      { label: 'Disease', color: '#9333ea', stroke: '#c084fc' },
    ].forEach(({ label: lbl, color, stroke }, i) => {
      const row = legend.append('g').attr('transform', `translate(0,${i * 22})`)
      row.append('circle').attr('r', 7).attr('cx', 7).attr('cy', 7)
        .attr('fill', color).attr('stroke', stroke).attr('stroke-width', 1.5)
      row.append('text').attr('x', 20).attr('y', 11)
        .attr('fill', '#94a3b8').attr('font-size', 11)
        .text(lbl)
    })

    return () => {
      simulation.stop()
      tooltip.remove()
    }
  }, [data, width, height])

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="w-full rounded-xl border border-surface-border bg-surface"
      style={{ minHeight: height }}
    />
  )
}
