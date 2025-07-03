#!/usr/bin/env node

/**
 * KnowledgePersistence-AI MCP Server
 * Model Context Protocol server for AI knowledge persistence
 * 
 * Provides seamless knowledge storage and retrieval for Claude Code sessions
 * Connects to PostgreSQL database with pgvector for semantic search
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import pg from 'pg';
import { OpenAI } from 'openai';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const { Pool } = pg;

class KnowledgePersistenceServer {
  constructor() {
    this.server = new Server(
      {
        name: 'knowledge-persistence-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Database connection
    this.db = new Pool({
      connectionString: process.env.DATABASE_URL || 'postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence',
      ssl: false,
    });

    // OpenAI client for embeddings
    this.openai = process.env.OPENAI_API_KEY ? new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    }) : null;

    // Current session tracking
    this.currentSessionId = process.env.SESSION_ID || uuidv4();

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'start_session',
            description: 'Start a new AI session with project context',
            inputSchema: {
              type: 'object',
              properties: {
                project_context: {
                  type: 'string',
                  description: 'Project context description'
                }
              },
              required: ['project_context']
            }
          },
          {
            name: 'get_contextual_knowledge',
            description: 'Retrieve contextual knowledge for current situation',
            inputSchema: {
              type: 'object',
              properties: {
                situation: {
                  type: 'string',
                  description: 'Description of current situation'
                },
                max_results: {
                  type: 'number',
                  description: 'Maximum number of results to return',
                  default: 10
                }
              },
              required: ['situation']
            }
          },
          {
            name: 'search_similar_knowledge',
            description: 'Search for similar knowledge using semantic similarity',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query'
                },
                knowledge_type: {
                  type: 'string',
                  description: 'Type of knowledge to search for',
                  enum: ['factual', 'procedural', 'contextual', 'relational', 'experiential', 'technical_discovery']
                },
                max_results: {
                  type: 'number',
                  description: 'Maximum number of results to return',
                  default: 10
                }
              },
              required: ['query']
            }
          },
          {
            name: 'store_knowledge',
            description: 'Store new knowledge item in the database',
            inputSchema: {
              type: 'object',
              properties: {
                knowledge_type: {
                  type: 'string',
                  enum: ['factual', 'procedural', 'contextual', 'relational', 'experiential', 'technical_discovery']
                },
                category: {
                  type: 'string',
                  description: 'Knowledge category'
                },
                title: {
                  type: 'string',
                  description: 'Knowledge title'
                },
                content: {
                  type: 'string',
                  description: 'Knowledge content'
                },
                context_data: {
                  type: 'object',
                  description: 'Additional context information'
                },
                retrieval_triggers: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Keywords that should trigger this knowledge'
                }
              },
              required: ['knowledge_type', 'category', 'title', 'content']
            }
          },
          {
            name: 'get_technical_gotchas',
            description: 'Get technical gotchas/solutions for similar problems',
            inputSchema: {
              type: 'object',
              properties: {
                problem_signature: {
                  type: 'string',
                  description: 'Description of the technical problem'
                },
                max_results: {
                  type: 'number',
                  description: 'Maximum number of results to return',
                  default: 5
                }
              },
              required: ['problem_signature']
            }
          },
          {
            name: 'store_technical_discovery',
            description: 'Store a technical discovery/gotcha for future reference',
            inputSchema: {
              type: 'object',
              properties: {
                problem: {
                  type: 'string',
                  description: 'Problem description'
                },
                solution: {
                  type: 'string',
                  description: 'Solution description'
                },
                context: {
                  type: 'object',
                  description: 'Additional context information'
                }
              },
              required: ['problem', 'solution']
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'start_session':
            return await this.startSession(args.project_context);

          case 'get_contextual_knowledge':
            return await this.getContextualKnowledge(args.situation, args.max_results);

          case 'search_similar_knowledge':
            return await this.searchSimilarKnowledge(args.query, args.knowledge_type, args.max_results);

          case 'store_knowledge':
            return await this.storeKnowledge(args);

          case 'get_technical_gotchas':
            return await this.getTechnicalGotchas(args.problem_signature, args.max_results);

          case 'store_technical_discovery':
            return await this.storeTechnicalDiscovery(args.problem, args.solution, args.context);

          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Error executing tool ${name}: ${error.message}`
        );
      }
    });
  }

  // Generate embedding for semantic search
  async generateEmbedding(text) {
    if (!this.openai) {
      return null; // Return null if OpenAI API key not configured
    }

    try {
      const response = await this.openai.embeddings.create({
        model: "text-embedding-3-small",
        input: text,
        encoding_format: "float"
      });
      return response.data[0].embedding;
    } catch (error) {
      console.error('Error generating embedding:', error.message);
      return null;
    }
  }

  // Start a new session
  async startSession(projectContext) {
    const sessionId = uuidv4();
    this.currentSessionId = sessionId;

    try {
      // Create session record
      const sessionResult = await this.db.query(`
        INSERT INTO ai_sessions (session_identifier, project_context, start_time)
        VALUES ($1, $2, NOW())
        RETURNING *
      `, [sessionId, projectContext]);

      // Get contextual startup knowledge
      const startupKnowledge = await this.getContextualKnowledge(
        `session_startup project_${projectContext}`,
        10
      );

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            session_id: sessionId,
            project_context: projectContext,
            startup_knowledge: startupKnowledge.content?.[0]?.text ? 
              JSON.parse(startupKnowledge.content[0].text) : [],
            status: 'Session started successfully'
          }, null, 2)
        }]
      };
    } catch (error) {
      throw new Error(`Failed to start session: ${error.message}`);
    }
  }

  // Get contextual knowledge
  async getContextualKnowledge(situation, maxResults = 10) {
    try {
      // First try basic text search
      const textSearchResult = await this.db.query(`
        SELECT k.*, s.session_identifier
        FROM knowledge_items k
        LEFT JOIN session_knowledge_links skl ON k.id = skl.knowledge_id
        LEFT JOIN ai_sessions s ON skl.session_id = s.id
        WHERE k.content ILIKE $1 
           OR k.title ILIKE $1 
           OR k.category ILIKE $1
           OR EXISTS (
             SELECT 1 FROM unnest(k.retrieval_triggers) AS trigger
             WHERE trigger ILIKE $1
           )
        ORDER BY k.importance_score DESC, k.created_at DESC
        LIMIT $2
      `, [`%${situation}%`, maxResults]);

      // If we have OpenAI API and no results from text search, try semantic search
      if (textSearchResult.rows.length === 0 && this.openai) {
        const embedding = await this.generateEmbedding(situation);
        if (embedding) {
          const semanticResult = await this.db.query(`
            SELECT k.*, s.session_identifier
            FROM knowledge_items k
            LEFT JOIN session_knowledge_links skl ON k.id = skl.knowledge_id
            LEFT JOIN ai_sessions s ON skl.session_id = s.id
            WHERE k.content_embedding IS NOT NULL
            ORDER BY k.content_embedding <-> $1::vector
            LIMIT $2
          `, [JSON.stringify(embedding), maxResults]);
          
          return {
            content: [{
              type: 'text',
              text: JSON.stringify(semanticResult.rows, null, 2)
            }]
          };
        }
      }

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(textSearchResult.rows, null, 2)
        }]
      };
    } catch (error) {
      throw new Error(`Failed to get contextual knowledge: ${error.message}`);
    }
  }

  // Search similar knowledge
  async searchSimilarKnowledge(query, knowledgeType, maxResults = 10) {
    try {
      let whereClause = '';
      let params = [`%${query}%`, maxResults];

      if (knowledgeType) {
        whereClause = 'AND k.knowledge_type = $3';
        params.push(knowledgeType);
      }

      const result = await this.db.query(`
        SELECT k.*, s.session_identifier
        FROM knowledge_items k
        LEFT JOIN session_knowledge_links skl ON k.id = skl.knowledge_id
        LEFT JOIN ai_sessions s ON skl.session_id = s.id
        WHERE (k.content ILIKE $1 OR k.title ILIKE $1 OR k.category ILIKE $1) 
        ${whereClause}
        ORDER BY k.importance_score DESC, k.created_at DESC
        LIMIT $2
      `, params);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result.rows, null, 2)
        }]
      };
    } catch (error) {
      throw new Error(`Failed to search similar knowledge: ${error.message}`);
    }
  }

  // Store new knowledge
  async storeKnowledge(knowledgeData) {
    try {
      const knowledgeId = uuidv4();
      
      // Generate embedding if OpenAI is available
      const embedding = await this.generateEmbedding(
        `${knowledgeData.title} ${knowledgeData.content}`
      );

      // Store knowledge item
      const result = await this.db.query(`
        INSERT INTO knowledge_items (
          id, knowledge_type, category, title, content,
          context_data, retrieval_triggers, content_embedding,
          importance_score, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        RETURNING *
      `, [
        knowledgeId,
        knowledgeData.knowledge_type,
        knowledgeData.category,
        knowledgeData.title,
        knowledgeData.content,
        JSON.stringify(knowledgeData.context_data || {}),
        knowledgeData.retrieval_triggers || [],
        embedding ? JSON.stringify(embedding) : null,
        75 // Default importance score
      ]);

      // Link to current session if we have one
      if (this.currentSessionId) {
        await this.db.query(`
          INSERT INTO session_knowledge_links (session_id, knowledge_id, interaction_type, created_at)
          SELECT s.id, $1, 'stored', NOW()
          FROM ai_sessions s 
          WHERE s.session_identifier = $2
        `, [knowledgeId, this.currentSessionId]);
      }

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'Knowledge stored successfully',
            knowledge_id: knowledgeId,
            knowledge_item: result.rows[0]
          }, null, 2)
        }]
      };
    } catch (error) {
      throw new Error(`Failed to store knowledge: ${error.message}`);
    }
  }

  // Get technical gotchas
  async getTechnicalGotchas(problemSignature, maxResults = 5) {
    try {
      const result = await this.db.query(`
        SELECT *
        FROM technical_gotchas
        WHERE problem_signature ILIKE $1 
           OR problem_description ILIKE $1
           OR working_solution ILIKE $1
           OR problem_context::text ILIKE $1
        ORDER BY frequency_encountered DESC, last_encountered DESC
        LIMIT $2
      `, [`%${problemSignature}%`, maxResults]);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result.rows, null, 2)
        }]
      };
    } catch (error) {
      throw new Error(`Failed to get technical gotchas: ${error.message}`);
    }
  }

  // Store technical discovery
  async storeTechnicalDiscovery(problem, solution, context = {}) {
    try {
      const gotchaId = uuidv4();

      const result = await this.db.query(`
        INSERT INTO technical_gotchas (
          id, problem_signature, problem_description, working_solution, problem_context,
          frequency_encountered, last_encountered
        ) VALUES ($1, $2, $3, $4, $5, 1, NOW())
        RETURNING *
      `, [
        gotchaId,
        problem,
        problem, // Use problem as description for now
        solution,
        JSON.stringify(context)
      ]);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'Technical discovery stored successfully',
            gotcha_id: gotchaId,
            technical_gotcha: result.rows[0]
          }, null, 2)
        }]
      };
    } catch (error) {
      throw new Error(`Failed to store technical discovery: ${error.message}`);
    }
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      await this.db.end();
      process.exit(0);
    });
  }

  async run() {
    // Test database connection
    try {
      await this.db.query('SELECT 1');
      console.error('Database connection established');
    } catch (error) {
      console.error('Database connection failed:', error.message);
      process.exit(1);
    }

    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('KnowledgePersistence-AI MCP Server running on stdio');
  }
}

// Start the server
const server = new KnowledgePersistenceServer();
server.run().catch(console.error);